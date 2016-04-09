from os.path import join

from .contrib.assets import Assets as AssetsMgr

from ..exports import ListCollector


class Assets(ListCollector):
    """
    This class manages component static assets.
    """
    def __init__(self, supervisor):
        super(Assets, self).__init__(supervisor)
        self.root = self.supervisor.config['root']
        self.debug = self.supervisor.config['assets.debug']
        self.url = self.supervisor.config['assets.url']
        assets_dir = self.supervisor.config['assets.directory']
        self.output = join(self.root, assets_dir)
        self.assets = AssetsMgr(directory=self.output, url=self.url,
                                debug=self.debug)
        self.bundles = {'js': {}, 'css': {}}
        self.sources = []

    def collect(self, component):
        assets_dir = component.get_export('static_dir', 'static')
        jsdir = component.pkgpath(join(assets_dir, 'js'), noerror=True)
        cssdir = component.pkgpath(join(assets_dir, 'css'), noerror=True)
        jsbundles = component.get_export('js_bundles', [])
        cssbundles = component.get_export('css_bundles', [])
        self.register((jsdir, cssdir, jsbundles, cssbundles))

    @staticmethod
    def parse_bundle(bundle):
        target, sources = bundle.split(':')
        target = target.strip()
        sources = [s.strip() for s in sources.split(',')]
        return target, sources

    def install_bundles(self, dir, bundles, bundle_type):
        if not all([dir, bundles]):
            return
        self.sources.append(dir)
        bundle_dict = self.bundles[bundle_type]
        for target, sources in (self.parse_bundle(b) for b in bundles):
            bundle_dict.set_default(target, [])
            bundle_dict[target].extend(sources)

    def install_member(self, assets):
        jsdir, cssdir, jsbundles, cssbundles = assets
        self.install_bundles(jsdir, jsbundles, 'js')
        self.install_bundles(cssdir, cssbundles, 'css')

    def post_install(self):
        for d in self.sources:
            self.assets.add_static_source(d)
        for target, sources in self.bundles['js'].items():
            self.assets.add_js_bundle(target, sources)
        for target, sources in self.bundles['css'].items():
            self.assets.add_css_bundle(target, sources)
