from ..data.state.provider import StateProvider


class ONDDProvider(StateProvider):
    name = 'ondd'
    allowed_methods = 'rw'
