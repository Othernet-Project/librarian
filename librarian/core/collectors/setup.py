from ...data.setup import Setup, SetupWizard
from ..exports import ObjectCollectorMixin, ListCollector
from ..exts import ext_container as exts


class AutoConfigurator(ObjectCollectorMixin, ListCollector):
    """
    Collects auto configurators for the setup module.
    """
    export_key = 'auto_config'

    def __init__(self, supervisor):
        super(AutoConfigurator, self).__init__(supervisor)
        exts.setup = Setup(exts.config['setup.file'])

    def install_member(self, auto_configurator):
        exts.setup.autoconfigure(auto_configurator.key, auto_configurator.fn)

    def post_install(self):
        exts.setup.load()


class Wizard(ObjectCollectorMixin, ListCollector):
    """
    Collects steps for the setup wizard.
    """
    export_key = 'wizard'

    def __init__(self, supervisor):
        super(Wizard, self).__init__(supervisor)
        exts.setup_wizard = SetupWizard(name='setup')

    def install_member(self, step_cls):
        exts.setup_wizard.register_class(step_cls)
