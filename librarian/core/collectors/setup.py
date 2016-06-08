from ...data.setup import Setup as SetupService, SetupWizard
from ..exports import ObjectCollectorMixin, ListCollector
from ..exts import ext_container as exts


class Setup(ObjectCollectorMixin, ListCollector):
    """
    Collects steps for the setup wizard.
    """
    export_key = 'setup'

    def __init__(self, supervisor):
        super(Setup, self).__init__(supervisor)
        exts.setup = SetupService()
        exts.setup_wizard = SetupWizard(name='setup')

    def install_member(self, step_cls):
        exts.setup_wizard.register_class(step_cls)
