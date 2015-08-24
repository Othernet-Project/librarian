import os
import glob
import logging

import webassets.script


def rebuild_assets(supervisor):
    print("Rebuilding assets")
    config = supervisor.config.copy()
    config['assets.debug'] = True
    assets_dir = supervisor.assets.env.directory
    # Remove existing assets
    for name, bundle in supervisor.assets.env._named_bundles.items():
        path = os.path.join(assets_dir, bundle.output) % {'version': '*'}
        for p in glob.iglob(path):
            os.unlink(p)
    env = webassets.script.CommandLineEnvironment(supervisor.assets.env,
                                                  logging.getLogger('assets'))
    env.invoke('build', {})
    raise supervisor.EarlyExit("Static assets rebuilt successfully",
                               exit_code=0)
