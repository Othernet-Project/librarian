from ..contrib.templates.decorators import template_helper
from ..exports import (ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector)
from ...data.state.container import StateContainer


class StateProviders(ObjectCollectorMixin, RegistryInstallerMixin,
                     ListCollector):
    """
    Collect state providers from components.
    """
    export_key = 'state'
    registry_class = StateContainer
    ext_name = 'state'

    def __init__(self, *args, **kwargs):
        super(StateProviders, self).__init__(*args, **kwargs)
        template_helper('state')(self.regobj)
