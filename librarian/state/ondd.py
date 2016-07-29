from ..data.state.provider import StateProvider


class ONDDCacheProvider(StateProvider):
    name = 'ondd_cache'
    allowed_methods = 'rw'
