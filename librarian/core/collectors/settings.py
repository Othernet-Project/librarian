from ..exports import (ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector)
from ...presentation.settings import SettingsManager


class Settings(ObjectCollectorMixin, RegistryInstallerMixin, ListCollector):
    """
    Collect settings fields from components.
    """
    export_key = 'settings'
    registry_class = SettingsManager
    ext_name = 'settings'
