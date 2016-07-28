from streamline import NonIterableRouteBase

from ..core.exts import ext_container as exts
from ..utils.route_mixins import JSONResponseMixin


class StateRoute(JSONResponseMixin, NonIterableRouteBase):
    name = 'state:handler'
    path = '/state/'

    def get(self):
        providers = exts.state.fetch_changes()
        return dict((key, prov.get()) for (key, prov) in providers.items())
