from ..exports import ListCollector


class Configuration(ListCollector):
    """
    This class manages component-specific configuration.
    """
    def collect(self, component):
        self.register(component)

    def install_member(self, component):
        for k, v in component.config.items():
            if k.startswith('exports.'):
                # Omit exports from master configuration
                continue
            self.supervisor.config[k] = v
