from ..exports import (ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector)
from ...data.state.container import StateContainer


class StateProviders(ObjectCollectorMixin, RegistryInstallerMixin,
                     ListCollector):
    """
    Collect state providers from components.
    """
    export_key = 'states'
    registry_class = StateContainer
    ext_name = 'states'
