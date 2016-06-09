import os
import glob
import logging
import shutil

import webassets.script

from ...exceptions import EarlyExit
from ...exts import ext_container as exts


def copytree(src, dst, symlinks=False, ignore=None, root='.'):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        if os.path.relpath(s, root) not in ignore:
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                copytree(s, d, symlinks=symlinks, ignore=ignore, root=root)
            else:
                if (not os.path.exists(d) or
                        os.stat(s).st_mtime - os.stat(d).st_mtime > 1):
                    shutil.copy2(s, d)


def check_collector_group(event, group_type):
    return group_type == 'assets'


class RebuildAssetsCommand(object):
    name = 'assets'
    flags = '--assets'
    kwargs = {
        'action': 'store_true',
        'help': 'rebuild static assets'
    }

    def run(self, args):
        exts.events.subscribe('exp.installed', self.rebuild,
                              condition=check_collector_group)

    def rebuild(self, *args, **kwargs):
        print("Rebuilding assets")
        config = exts.config.copy()
        config['assets.debug'] = True
        assets_dir = exts.assets.env.directory
        # Remove existing assets
        for name, bundle in exts.assets.env._named_bundles.items():
            path = os.path.join(assets_dir, bundle.output) % {'version': '*'}
            for p in glob.iglob(path):
                os.unlink(p)
        logger = logging.getLogger('assets')
        env = webassets.script.CommandLineEnvironment(exts.assets.env, logger)
        env.invoke('build', {})
        raise EarlyExit("Static assets rebuilt successfully", exit_code=0)


class CollectAssetsCommand(object):
    name = 'collect'
    flags = '--collect'
    kwargs = {
        'action': 'store_true',
        'help': 'collect static assets',
    }

    def run(self, args):
        exts.events.subscribe('exp.installed', self.collect,
                              condition=check_collector_group)

    def collect(self, *args, **kwargs):
        print("Collecting assets")
        bundles = exts.assets.env._named_bundles.values()
        bundled_assets = [name for bundle in bundles
                          for name, path in bundle.resolve_contents()]
        assets_dir = exts.assets.env.directory
        asset_sources = exts.config.get('assets.sources', {})
        for path, url in asset_sources.values():
            for subdir in os.listdir(path):
                subpath = os.path.join(path, subdir)
                if os.path.isdir(subpath):
                    copytree(subpath,
                             os.path.join(assets_dir, subdir),
                             ignore=bundled_assets,
                             root=subpath)
        raise EarlyExit("Static assets collected successfully", exit_code=0)
