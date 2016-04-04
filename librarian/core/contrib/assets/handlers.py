import os
import glob
import logging
import shutil

import webassets.script


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


def rebuild_assets(arg, supervisor):
    print("Rebuilding assets")
    config = supervisor.config.copy()
    config['assets.debug'] = True
    assets_dir = supervisor.exts.assets.env.directory
    # Remove existing assets
    for name, bundle in supervisor.exts.assets.env._named_bundles.items():
        path = os.path.join(assets_dir, bundle.output) % {'version': '*'}
        for p in glob.iglob(path):
            os.unlink(p)
    env = webassets.script.CommandLineEnvironment(supervisor.exts.assets.env,
                                                  logging.getLogger('assets'))
    env.invoke('build', {})
    raise supervisor.EarlyExit("Static assets rebuilt successfully",
                               exit_code=0)


def collect_assets(arg, supervisor):
    print("Collecting assets")
    bundles = supervisor.exts.assets.env._named_bundles.values()
    bundled_assets = [name for bundle in bundles
                      for name, path in bundle.resolve_contents()]

    assets_dir = supervisor.exts.assets.env.directory
    asset_sources = supervisor.config.get('assets.sources', {})
    for path, url in asset_sources.values():
        for subdir in os.listdir(path):
            subpath = os.path.join(path, subdir)
            if os.path.isdir(subpath):
                copytree(subpath,
                         os.path.join(assets_dir, subdir),
                         ignore=bundled_assets,
                         root=subpath)

    raise supervisor.EarlyExit("Static assets collected successfully",
                               exit_code=0)
