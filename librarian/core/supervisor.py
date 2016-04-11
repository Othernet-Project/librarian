import logging
import os
import sys

from bottle import Bottle
from gevent import pywsgi, sleep
from confloader import get_config_path, ConfDict

from .dependencies import DependencyLoader
from .exts import ext_container
from .logs import configure_logger
from .pubsub import PubSub
from .signal_handlers import on_interrupt


class EarlyExit(Exception):

    def __init__(self, message='', exit_code=0):
        super(EarlyExit, self).__init__(message)
        self.exit_code = exit_code


class Supervisor:
    #: Interval of the background loop in seconds. This is the possible
    #: shortest time in between consecutive execution of background tasks.
    LOOP_INTERVAL = 5

    #: Default name of the application configuration file.
    DEFAULT_CONFIG_FILENAME = 'config.ini'

    #: Default configuration.
    CONFIG_DEFAULTS = {
        'autojson': True,
        'catchall': True
    }

    # Aliases for system events

    #: Component is initializing
    INITIALIZE = 'initialize'

    #: Component finished loading
    COMPONENT_MEMBER_LOADED = 'component_member_loaded'

    #: All components finished loading
    INIT_COMPLETE = 'init_complete'

    #: Server is about to start
    PRE_START = 'pre_start'

    #: Server has started
    POST_START = 'post_start'

    #: New background loop cycle
    BACKGROUND = 'background'

    #: Server is about to go down
    SHUTDOWN = 'shutdown'

    #: Server is about to go down in an emergency
    IMMEDIATE_SHUTDOWN = 'immediate_shutdown'

    #: List of all events
    APP_HOOKS = (
        INITIALIZE,
        COMPONENT_MEMBER_LOADED,
        INIT_COMPLETE,
        PRE_START,
        POST_START,
        BACKGROUND,
        SHUTDOWN,
        IMMEDIATE_SHUTDOWN,
    )

    #: Name of the root package that contains the supervisor
    ROOT_PKG = __name__.split('.')[0]

    #: List of core components
    CORE_COMPONENTS = (
        'assets',
        'system',
        'commands',
        'databases',
        'sessions',
        'auth',
        'i18n',
        'cache',
        'tasks',
        'templates',
    )

    EarlyExit = EarlyExit

    def __init__(self, root_dir):
        self.server = None
        self.app = self.wsgi = Bottle()
        self.app.supervisor = self
        self.exts = ext_container
        self.exts.events = PubSub()
        self.configure(root_dir)
        self.configure_logger()
        self.load_components()
        self.handle_interrupt()
        self.running = True
        self.finalize()

    def load_config(self, path, strict=True):
        path = os.path.abspath(path)
        if not strict and not os.path.exists(path):
            return ConfDict()
        return ConfDict.from_file(path, defaults=self.CONFIG_DEFAULTS)

    def merge_config(self, config):
        # merge component config into global config, but without overwriting
        # existing data
        self.config.setdefaults(config)

    def configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        self.config = self.app.config = self._load_config(self.config_path)
        self.config['root'] = root_dir
        self.exts.config = self.config

    def configure_logger(self):
        configure_logger(self.config)

    def install_hook(self, name, handler, mod_name=None, **kwargs):
        """
        Install an event hander for given event name. For
        :py:attr:`~Supervisor.INITIALIZE` events, ``mod_name`` argument must
        also be passed, and the event is fired immediately for any listeners
        that are subscribed to it.

        .. note::
            The :py:attr:`~Supervisor.INITIALIZE` events are always fired only
            for the specific module, not as a global event.

        This method is invoked by
        :py:meth:`Supervisor.install_component_member` method. Extra keyword
        arguments are accepted but ignored, to remain compatible with the
        caller's API.
        """
        self.exts.events.subscribe(name, handler)
        # the initialize hook must be fired immediately in the scope to
        # which it belongs only
        if name == self.INITIALIZE:
            if not mod_name:
                raise TypeError('For INITIALIZE event, mod_name is required')
            self.exts.events.publish(name, self, scope=mod_name)

    def install_routes(self, factory, **kwargs):
        """
        Install routes returned by a route configuration factory function. The
        ``factory`` argument is a function that accept a single positional
        argument which is the supervisor configuration dictionary. It is
        expected to return an interable where each element is an iterable
        containing the following five elements:

        - route name
        - handler callable
        - method(s)
        - path
        - dict of extra keyword arguments

        These elements match the arguments passed to
        :py:meth:`bottle.Bottle.route` method.

        This method is invoked by
        :py:meth:`Supervisor.install_component_member` method. Extra keyword
        arguments are accepted but ignored, to remain compatible with the
        caller's API.
        """
        route_config = factory(self.config)
        for route in route_config:
            (name, handler, method, path, kwargs) = route
            self.app.route(path, method, handler, name=name, **kwargs)

    def install_plugin(self, factory, **kwargs):
        """
        Install a plugin returned by a plugin factory function. The ``factory``
        argument is expected to be a callable that takes the supervisor
        instance as its only argument, and returns a plugin object compatible
        with bottle plugin API.

        More information about the plugin API can be found `in the bottle
        documentation <http://bottlepy.org/docs/dev/plugindev.html>`_.

        This method is invoked by
        :py:meth:`Supervisor.install_component_member` method. Extra keyword
        arguments are accepted but ignored, to remain compatible with the
        caller's API.
        """
        plugin = factory(self)
        self.app.install(plugin)

    #: Information for handling component installation. The top-level keys are
    #: component member types as returned by the dependency resolver. Each type
    #: has three subkeys:
    #:
    #: - ``exports``: default exports for a module
    #: - ``is_strict``: whether exports must exist
    #: - ``handler``: a method that handles the installation
    #:
    #: 'Exports' are objects that a component member makes available to the
    #: supervisor. The nature of the objects depend on the the component member
    #: type (e.g., exports for a hooks are hook types found in the
    #: :py:attr:`~Supervisor.APPHOOKS.` attribute). The ``'exports'`` key
    #: provides the defaults for members that do not specify any exports.
    #:
    #: When ``is_strict`` flag is set for a particular member type, all exports
    #: must exist.
    #:
    COMPONENT_META = {
        'hooks': {
            'exports': dict(zip(APP_HOOKS, [{}] * len(APP_HOOKS))),
            'is_strict': False,
            'handler': install_hook
        },
        'plugins': {
            'exports': {
                'plugin': {}
            },
            'is_strict': True,
            'handler': install_plugin
        },
        'routes': {
            'exports': {
                'routes': {}
            },
            'is_strict': True,
            'handler': install_routes
        }
    }

    def install_component_member(self, member):
        """
        Install a component members using information provided by the
        :py:attr:`~Supervisor.CONTENT_META` dict. The component members are
        expected to be dict-like objects that have a ``'name'``, ``'type'``,
        and ``'pkg_path'`` keys.
        """
        member_type = member['type']
        pkg_path = member['pkg_path']
        handler = self.COMPONENT_META[member_type]['handler']
        member_conf = os.path.join(pkg_path, self.DEFAULT_CONFIG_FILENAME)
        config = self.config.import_from_file(member_conf, as_defaults=True,
                                              ignore_missing=True)
        handler(self, **member)
        # notify possibly other components that a new component has been
        # installed successfully
        self.exts.events.publish(self.COMPONENT_MEMBER_LOADED,
                                 self,
                                 member=member,
                                 config=config)
        logging.debug("LOADED: {0}".format('::'.join([member['pkg_path'],
                                                      member['name']])))

    def get_core_components(self):
        """
        Return a list of import paths for all core components listed in the
        :py:attr:`~Supervisor.CORE_COMPONENTS` list.
        """
        return ['.'.join([__package__, 'contrib', name])
                for name in self.CORE_COMPONENTS]

    def get_component_list(self):
        """
        Return a list of all components that should be loaded. Components are
        listed as package names that contain them.

        Root package, that is the package that contains this supervisor, will
        always be included before any package listed in ``app.components`` list
        in the application configuration.

        Unless application configuration sets an ``app.core_override`` package,
        the core components specified in :py:attr:`~Supervisor.CORE_COMPONENTS`
        attribute will be loaded before all other components.
        """
        components = [self.ROOT_PKG]
        components.extend(self.config.get('app.components', []))
        if not self.config.get('app.core_override'):
            # Configuration does not specify that core is overridden by 3rd
            # party components, so we need to load the core first.
            components = self.get_core_components() + components
        return components

    def load_components(self):
        """
        Load all components based on the list returned by
        :py:meth:`~Supervisor._get_component_list()`. The component list is
        wrapped in dependency resolver class to facilitate ordering of loads.
        """
        components = self._get_component_list()
        loader = DependencyLoader(components, self.COMPONENT_META)
        for member in loader.load():
            try:
                self.install_component_member(member)
            except Exception:
                logging.exception('Component member installation failed.')

    def handle_interrupt(self):
        """
        Register INT signal handler.
        """
        on_interrupt(self.halt)

    def enter_background_loop(self):
        """
        Keep emitting the :py:attr:`~Supervisor.BACKGROUND` event as long as
        :py:attr:`~Supervisor._running` flag is ``True``. The interval in which
        the events are emitted is roughly :py:attr:`~Supervisor.LOOP_INTERVAL`
        seconds.
        """
        while self._running:
            sleep(self.LOOP_INTERVAL)
            # Fire background event
            self.exts.events.publish(self.BACKGROUND, self)

    def finalize(self):
        """
        Finalize supervisor's initialization and announce the
        :py:attr:`~Supervisor.INIT_COMPLETE` event.

        If any of the components raise an :py:exc:`EarlyExit` exception during
        this stage, the system will exit. This exception is a normal
        flow-control mechanism, not an error condition.

        Exceptions other than :py:exc:`EarlyExit` are logged and reraised.
        """
        try:
            # Fire init-complete event. Command line handlers should be
            # executed at this point.
            self.exts.events.publish(self.INIT_COMPLETE, self)
        except EarlyExit as exc:
            # One of the command line handlers probably requested early exit
            sys.exit(exc.exit_code)
        except Exception:
            logging.exception("An error occurred during `init_complete`.")
            raise

    def start(self):
        # Fire pre-start event right before starting the WSGI server.
        self.exts.events.publish(self.PRE_START, self)
        host = self.config['app.bind']
        port = self.config['app.port']
        self.server = pywsgi.WSGIServer((host, port), self.wsgi, log=None)
        self.server.start()  # non-blocking
        assert self.server.started, 'Expected server to be running'
        logging.debug("Started server on http://%s:%s/", host, port)
        print('Started server on http://%s:%s/' % (host, port))
        # Fire post-start event after WSGI server is started.
        self.exts.events.publish(self.POST_START, self)
        # Start background loop
        self._enter_background_loop()

    def halt(self):
        logging.info('Stopping the application.')
        self._running = False
        self.server.stop(5)
        logging.info('Running shutdown hooks.')
        self.exts.events.publish(self.SHUTDOWN, self)
        logging.info('Clean shutdown.')
