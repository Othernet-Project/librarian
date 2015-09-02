import collections
import importlib
import logging
import os
import pkgutil
import sys


class UnresolvableDependency(Exception):
    """Exception raised if a component referenced as another's dependency is
    not found on the list of installable components."""
    pass


class CircularDependency(Exception):
    """Exception raised if circular dependencies are encountered."""
    pass


class DependencyNotFound(Exception):
    """Exception raised if a dependency cannot be loaded."""
    pass


def module_name(mod):
    return mod.__name__.split('.')[-1]


class DependencyLoader(object):
    """Components may define an `EXPORTS` section in each of their significant
    modules, which are inspected during component loading. If it's omitted, a
    default configuration is being used for component discovery. Example
    configuration:

    ``hooks.py``
    EXPORTS = {
        'pre_init': {
            'depends_on': ['other_pkg.mod_name.fn_name', 'some.mod.fn'],
            'required_by': ['first_pkg.a_mod.a_fn']
        }
    }
    """
    def __init__(self, components, component_meta):
        self._components = components
        self._component_meta = component_meta
        self._dep_tree = collections.OrderedDict()

    def _import_modules(self, pkg_name, whitelist=None):
        """
        :param pkg_name:   component package name (must be on pythonpath)
        :param whitelist:  list of modules to be imported only
        """
        pkg = importlib.import_module(pkg_name)
        pkg_path = os.path.dirname(os.path.abspath(pkg.__file__))
        if pkg_path not in sys.path:
            sys.path.append(pkg_path)

        is_broken = False
        modules = []
        for (loader, mod_name, is_pkg) in pkgutil.iter_modules([pkg_path]):
            if whitelist is None or mod_name in whitelist:
                mod_path = '.'.join([pkg_name, mod_name])
                try:
                    mod = importlib.import_module(mod_path)
                except Exception:
                    logging.exception("Component {0} encountered an error "
                                      "during it's loading, installation "
                                      "skipped.".format(pkg_name))
                    # make sure component won't be partially installed
                    modules = []
                    is_broken = True
                    break
                else:
                    modules.append(mod)

        return (pkg_path, modules, is_broken)

    def _get_exports_spec(self, module):
        try:
            exports = getattr(module, 'EXPORTS')
        except AttributeError:
            comp_meta = self._component_meta[module_name(module)]
            return (comp_meta['exports'], comp_meta['is_strict'])
        else:
            return (exports, True)

    def _build(self):
        """Assemble initial dependency tree, preserving the order as specified
        in the component list."""
        module_names = self._component_meta.keys()
        for pkg_name in self._components:
            (pkg_path, modules, is_broken) = self._import_modules(pkg_name,
                                                                  module_names)
            if not modules and not is_broken:
                # in case an installed app has no significant members for core
                # to be loaded, add a noop `initialize` hook so it will be
                # installed nevertheless
                dep_id = '{0}.hooks.initialize'.format(pkg_name)
                self._dep_tree[dep_id] = dict(fn=lambda x: x,
                                              name='initialize',
                                              type='hooks',
                                              pkg_name=pkg_name,
                                              pkg_path=pkg_path)
                continue
            # build initial unparsed and unordered dependency tree
            for mod in modules:
                exports, is_strict = self._get_exports_spec(mod)
                for (fn_name, dependencies) in exports.items():
                    try:
                        fn = getattr(mod, fn_name)
                    except AttributeError as exc:
                        if is_strict:
                            msg = '[{0}] {1}'.format(mod.__name__, exc)
                            raise DependencyNotFound(msg)
                        continue
                    else:
                        dep_id = '.'.join([fn.__module__, fn.__name__])
                        self._dep_tree[dep_id] = dict(fn=fn,
                                                      name=fn.__name__,
                                                      type=module_name(mod),
                                                      pkg_name=pkg_name,
                                                      pkg_path=pkg_path,
                                                      **dependencies)

    def _parse(self):
        """Generates reverse dependencies. Essentially turns `required_by`
        directives into the opposite direction, as `depends_on` specifications
        of the component they point to."""
        for (dep_id, dep) in self._dep_tree.items():
            for dependent_dep_id in dep.pop('required_by', []):
                try:
                    dependent_dep = self._dep_tree[dependent_dep_id]
                except KeyError as exc:
                    msg = "Dependency {0} is missing.".format(exc)
                    raise UnresolvableDependency(msg)
                else:
                    existing_deps = dependent_dep.get('depends_on', [])
                    deps = existing_deps + [dep_id]
                    self._dep_tree[dependent_dep_id]['depends_on'] = deps

    def _collect(self, dependent_id, collected=None):
        """Recursively assemble the list of dependencies."""
        if collected is None:
            collected = collections.deque([dependent_id])

        try:
            dependent = self._dep_tree[dependent_id]
        except KeyError as exc:
            msg = "Dependency {0} is missing.".format(exc)
            raise UnresolvableDependency(msg)
        else:
            for needed_dep_id in dependent.get('depends_on', []):
                if needed_dep_id in collected:
                    msg = 'Dependent module {0} referenced {1}'
                    raise CircularDependency(msg.format(dependent_id,
                                                        needed_dep_id))
                collected.appendleft(needed_dep_id)
                self._collect(needed_dep_id, collected=collected)

        return collected

    def _order(self):
        """Reorder the list of dependencies according to the results of the
        recursive dependency analysis."""
        ordered_deps = collections.OrderedDict()
        for dep_id in self._dep_tree:
            for needed_dep_id in self._collect(dep_id):
                if needed_dep_id not in ordered_deps:
                    ordered_deps[needed_dep_id] = self._dep_tree[needed_dep_id]

        self._dep_tree = ordered_deps

    def load(self):
        self._build()
        self._parse()
        self._order()
        return self._dep_tree.values()
