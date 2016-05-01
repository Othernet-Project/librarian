from ...core.utils import as_iterable


class FacetTypes:
    """
    Static class for querying meta information about facet types.
    """
    # Special purpose-meta types
    UPDATES = 'updates'
    # Actual facet types
    GENERIC = 'generic'
    HTML = 'html'
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    MAPPING = {
        GENERIC: 1,
        HTML: 2,
        VIDEO: 4,
        AUDIO: 8,
        IMAGE: 16,
    }
    SPECIAL_TYPES = [
        UPDATES,
    ]
    COMMON_KEYS = [
        'path',
        'facet_types',
    ]
    SPECIALIZED_KEYS = {
        GENERIC: [],
        AUDIO: [
            'author',
            'title',
            'album',
            'genre',
            'duration',
        ],
        VIDEO: [
            'author',
            'title',
            'description',
            'width',
            'height',
            'duration',
        ],
        IMAGE: [
            'title',
            'width',
            'height',
        ],
        HTML: [
            'author',
            'title',
            'description',
            'keywords',
            'language',
            'copyright',
            'outernet_formatting',
        ]
    }
    SEARCH_KEYS = {
        GENERIC: [],
        AUDIO: [
            'author',
            'title',
            'genre',
            'album',
        ],
        VIDEO: [
            'author',
            'title',
            'description',
        ],
        IMAGE: [
            'title',
        ],
        HTML: [
            'author',
            'title',
            'description',
            'keywords',
        ]
    }

    @classmethod
    @as_iterable(params=[1])
    def to_bitmask(cls, names):
        """
        Return bitmask for the given facet type name(s).
        """
        return sum(cls.MAPPING[name] for name in set(names))

    @classmethod
    def from_bitmask(cls, bitmask):
        """
        Return list of facet type names for a given bitmask.
        """
        return [name for (name, value) in cls.MAPPING.items()
                if bitmask & value == value]

    @classmethod
    def is_valid(cls, name):
        """
        Return whether the passed in facet type is valid or not by checking if
        it's present in the name / bitmask mapping.
        """
        return name in cls.MAPPING

    @classmethod
    def names(cls, include_meta=False):
        """
        Return a list of all known facet type names. If the ``include_meta``
        flag is set, special purpose facet type names will be included in the
        list.
        """
        names = cls.MAPPING.keys()
        if include_meta:
            names += cls.SPECIAL_TYPES
        return names

    @classmethod
    def keys(cls, for_type=None, specialized_only=False):
        """
        Return a list of keys that are relevant to the passed in facet type,
        or for all types in case ``for_type`` is ``None``. The flag
        ``specialized_only`` is used only if ``for_type`` was specified, in
        which case if it's set, no common keys will be included, only those
        specific to the given type.
        """
        keys = [] if specialized_only else cls.COMMON_KEYS
        if for_type:
            return keys + cls.SPECIALIZED_KEYS[for_type]
        # return a set of all facet keys collected for all types
        return set(sum(cls.SPECIALIZED_KEYS.values(), keys))

    @classmethod
    def search_keys(cls, for_type=None):
        """
        Return a list of keys that could hold relevant information for text
        based searches on a specific facet type, or for all types in case
        ``for_type`` is ``None``.
        """
        if for_type:
            return cls.SEARCH_KEYS[for_type]
        # return a set of all search keys collected for all types
        return set(sum(cls.SEARCH_KEYS.values(), []))
