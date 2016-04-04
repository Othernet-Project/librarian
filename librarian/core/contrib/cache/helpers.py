from .backends import BaseCache


class CacheConfigError(Exception):
    pass


def setup(backend, config):
    """Instantiate and return the requested cache backend.

    :param backend:  string: unique backend class identifier, possible values:
                     "in-memory", "memcached"
    :param config:   dict containing config params
    """
    options = dict()
    backends = dict((cls.identifier, cls) for cls in BaseCache.children())
    try:
        backend_cls = backends[backend]
    except KeyError:
        backend_cls = backends['noop']
    else:
        for name, validator in backend_cls.get_config_params().items():
            key = 'cache.{0}'.format(name)
            try:
                value = config[key]
            except KeyError:
                raise CacheConfigError("Cache[{0}] config parameter {1} is "
                                       "missing.".format(backend, key))
            else:
                try:
                    options[name] = validator(value)
                except ValueError as exc:
                    (error, validator_type) = exc.args
                    msg = ("Cache[{0}] config parameter {1} is invalid: "
                           "{2}".format(backend, key, error))
                    raise CacheConfigError(msg)

    return backend_cls(**options)
