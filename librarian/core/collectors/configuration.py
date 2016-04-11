from ..exports import ListCollector


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
            self.supervisor.config[k] = v
