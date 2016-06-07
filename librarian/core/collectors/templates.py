import os

import bottle

from ..exports import ListCollector


class Templates(ListCollector):
    """
    Collect and install component template roots.
    """
    DEFAULT_TEMPLATE_DIR = 'views'

    def __init__(self, supervisor):
        super(Templates, self).__init__(supervisor)
        self.root = self.supervisor.config['root']

    def collect(self, component):
        template_dir = component.get_export('template_dir',
                                            self.DEFAULT_TEMPLATE_DIR)
        template_path = os.path.join(component.pkgdir, template_dir)
        self.register(template_path)

    def install_member(self, template_path):
        bottle.TEMPLATE_PATH.insert(0, template_path)
