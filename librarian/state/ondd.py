from ..data.state.provider import StateProvider


class ONDDCacheProvider(StateProvider):
    name = 'ondd:cache'
    allowed_methods = 'rw'
