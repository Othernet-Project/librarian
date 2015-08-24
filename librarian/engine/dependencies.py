import collections
import importlib
import os
import pkgutil


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
    pkg = mod.__package__ or ''
    return mod.__name__.replace(pkg, '')


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
        modules = []
        for (loader, mod_name, is_pkg) in pkgutil.iter_modules(pkg_path):
            if whitelist is None or mod_name in whitelist:
                mod = loader.find_module(mod_name).load_module(mod_name)
                modules.append(mod)

        return modules

    def _get_exports_spec(self, module):
        try:
            exports = getattr(module, 'EXPORTS')
        except AttributeError:
            comp_meta = self._component_meta[module_name(module)]
            return (comp_meta['exports'], comp_meta['is_strict'])
        else:
            return (exports, True)

    def _build(self):
        # assemble a list of modules in the same order as their packages were
        # listed on the component list
        modules = []
        for pkg_name in self._components:
            modules += self._import_modules(pkg_name,
                                            self._component_meta.keys())
        # build initial unparsed and unordered dependency tree
        for mod in modules:
            exports, is_strict = self._get_exports_spec(mod)
            for (fn_name, dependencies) in exports.items():
                try:
                    fn = getattr(mod, fn_name)
                except AttributeError as exc:
                    if is_strict:
                        raise DependencyNotFound(exc)
                    continue
                else:
                    dep_id = '.'.join(fn.__module__, fn.__name__)
                    self._dep_tree[dep_id] = dict(fn=fn,
                                                  name=fn.__name__,
                                                  type=module_name(mod),
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
