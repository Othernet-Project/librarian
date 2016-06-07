from ..exports import ListCollector
from ..exts import ext_container as exts


class Configuration(ListCollector):
    """
    This class manages component-specific configuration.
    """
    def collect(self, component):
        self.register(component.config)

    def install_member(self, config):
        for k, v in config.items():
            if k.startswith('exports.'):
                # Omit exports from master configuration
                continue
            exts.config.setdefault(k, v)
