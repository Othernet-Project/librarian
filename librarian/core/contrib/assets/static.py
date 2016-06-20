import os

import webassets.script


class Assets:
    """
    Wrapper class for webassets.Environment
    """
    out_pattern = '{filetype}/{filename}-bundle-%(version)s.{filetype}'

    def __init__(self, directory='static', url='/static/', debug='merge'):
        self.directory = os.path.abspath(directory)
        self.url = url
        self.debug = debug
        self.env = self._env_factory(directory, url, debug)

    @staticmethod
    def _env_factory(directory, url, debug):
        """
        Create a ``webassets.Environment`` instance which will manage the
        assets for this object.
        """
        env = webassets.Environment(directory=directory, url=url, debug=debug,
                                    url_expire=True)
        env.append_path(directory, url=url)
        env.versions = 'hash'
        env.manifest = 'file'
        if not debug:
            env.auto_build = False
            # ^-- FIXME: kinda looks like it could be `env.auto_build = debug`
        return env

    def add_static_source(self, path, url=None):
        """
        Third parties should call this method to register their own static
        folders.
        """
        self.env.append_path(path, url=url)

    def add_js_bundle(self, out, assets):
        """
        Create and register a JavaScript bundle

        The ``out`` parameter is a path to the bundle. It does not include the
        ``js/`` path prefix nor the ``.js`` extension. These are added
        automatically by this method. For example, if you want to build a
        bundle in ``static/js/common/foo.js``, then you would set the ``out``
        argument to ``common/foo``. The ``%(version)s`` paceholder is
        automatically inserted into the resulting filename, so the complete
        path will be ``js/common/foo-%(version)s.js``.

        The ``out`` value is also used to identify bundles, and the identifier
        is prefixed with 'js/'.

        Assets is an iterable containing the bundle's contents. They must be
        specified in correct load order. Similar to output path, the asset
        paths are specified without the ``js/`` directory and ``.js``
        extension. These are appended to the paths autmatically.

        JavaScript assets use ``uglifyjs`` as filter.

        This method returns the ``Bundle`` object. Bundle object can be used
        for nesting within other bundles.
        """
        assets = [self._js_path(a) for a in self._unique(assets)]
        out_path = self.out_pattern.format(filetype='js', filename=out)
        bundle = webassets.Bundle(*assets, filters='rjsmin', output=out_path)
        self.env.register('js/' + out, bundle)
        return bundle

    def add_css_bundle(self, out, assets):
        """
        Create and register Compass bundle

        The ``out`` parameter is a path to bundle. It does not include the
        ``css/`` prefix nor ``.css`` extension. These are added automatically.
        For example, if you want to build a bundle in ``static/css/main.css``,
        then you would set the ``out`` argument to ``main``.

        The ``out`` value is also used to identify the bundle, and the
        identifier is prefixed with 'css/'.

        Assets is an iterable containing the bundle's contents. They must be
        specified in correct load order. Similar to output path, the asset
        paths are specified without the ``css/`` directory and ``.css``
        extension. These are appended to the paths autmatically.

        This method returns the ``Bundle`` object which can be used to nest
        within other bundles.
        """
        assets = [self._css_path(a) for a in self._unique(assets)]
        out_path = self.out_pattern.format(filetype='css', filename=out)
        bundle = webassets.Bundle(*assets, filters='cssmin', output=out_path)
        self.env.register('css/' + out, bundle)
        return bundle

    def get(self, name):
        return self.env[name].urls()[0]

    def __getitem__(self, name):
        return self.get(name)

    @staticmethod
    def _unique(seq):
        """
        Generator that yields elements of a sequence in order they appear
        without repeating already yielded elements.
        """
        seen = set()
        for i in seq:
            if i in seen:
                continue
            seen.add(i)
            yield i

    @staticmethod
    def _js_path(s):
        """
        Return a string with '.js' extension if input is a string, otherwise
        return input value verbatim.
        """
        if type(s) is str:
            return s + '.js'
        return s

    @staticmethod
    def _css_path(s):
        """
        Return a string with '.css' extension if input is a string, otherwise
        return input value verbatim.
        """
        if type(s) is str:
            return s + '.css'
        return s

    @staticmethod
    def parse_bundle(bundle):
        """
        Parse a bundle line. The bundle line has the folowing format:

        NAME: CONTENT

        NAME is a bundle name which will be used to get the bundle. When
        registering a bundle, 'js/' or 'css/' prefix will be prepended to NAME,
        depending on whether bundle is a JavaScript or CSS bundle.

        CONTENT is a comma-separated list of paths that comprise the bunde.
        Whitespace around commas is not significant (e.g., 'foo, bar' is the
        same as 'foo,bar', and same as 'foo , bar').
        """
        bundle_name, bundle_content = [b.strip() for b in bundle.split(':')]
        bundle_content = [b.strip() for b in bundle_content.split(',')]
        return bundle_name, bundle_content

    @classmethod
    def merge_bundles(cls, bundles):
        """
        Merge the values of the keys with the same name in a list of bundle
        dicts. Return value is a single dict.
        """
        merged = dict()
        for name, contents in [cls.parse_bundle(b) for b in bundles]:
            merged.setdefault(name, [])
            merged[name].extend(contents)
        return merged

    @classmethod
    def from_config(cls, config):
        """
        Create Assets instance from dict-like config object.
        """
        assets_dir = os.path.join(config['root'], config['assets.directory'])
        assets_url = config['assets.url']
        assets_debug = config['assets.debug']
        assets = cls(assets_dir, assets_url, assets_debug)
        asset_sources = config.get('assets.sources', {})
        for path, url in asset_sources.values():
            assets.add_static_source(os.path.join(path, 'css'), url=url)
            assets.add_static_source(os.path.join(path, 'js'), url=url)

        js_bundles = cls.merge_bundles(config.get('assets.js_bundles', []))
        for name, contents in js_bundles.items():
            assets.add_js_bundle(name, contents)

        css_bundles = cls.merge_bundles(config.get('assets.css_bundles', []))
        for name, contents in css_bundles.items():
            assets.add_css_bundle(name, contents)

        return assets
