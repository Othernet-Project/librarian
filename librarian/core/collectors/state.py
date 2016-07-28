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
