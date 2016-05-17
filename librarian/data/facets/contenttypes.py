from ...core.utils import as_iterable

try:
    unicode
except NameError:
    unicode = str


class ContentTypes:
    """
    Static class for querying meta information about content types.
    """
    GENERIC = 'generic'
    HTML = 'html'
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    DIRECTORY = 'directory'
    MAPPING = {
        GENERIC: 1,
        HTML: 2,
        VIDEO: 4,
        AUDIO: 8,
        IMAGE: 16,
        DIRECTORY: 32,
    }
    TYPES = {
        GENERIC: {},
        AUDIO: {
            'author': unicode,
            'title': unicode,
            'album': unicode,
            'genre': unicode,
            'duration': float,
        },
        VIDEO: {
            'author': unicode,
            'title': unicode,
            'description': unicode,
            'width': int,
            'height': int,
            'duration': float,
        },
        IMAGE: {
            'title': unicode,
            'width': int,
            'height': int,
        },
        HTML: {
            'author': unicode,
            'title': unicode,
            'description': unicode,
            'keywords': unicode,
            'language': unicode,
            'copyright': unicode,
            'outernet_formatting': int,
        },
        DIRECTORY: {
            'name': unicode,
            'description': unicode,
            'icon': unicode,
            'cover': unicode,
            'publisher': unicode,
            'keywords': unicode,
            'view': unicode,
            'main': unicode,
        }
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
        ],
        DIRECTORY: [
            'name',
            'description',
            'publisher',
            'keywords',
        ]
    }

    @classmethod
    @as_iterable(params=[1])
    def to_bitmask(cls, names):
        """
        Return bitmask for the given content type name(s).
        """
        return sum(cls.MAPPING[name] for name in set(names))

    @classmethod
    def from_bitmask(cls, bitmask):
        """
        Return list of content type names for a given bitmask.
        """
        return [name for (name, value) in cls.MAPPING.items()
                if bitmask & value == value]

    @classmethod
    def is_valid(cls, name):
        """
        Return whether the passed in content type is valid or not by checking
        if it's present in the name / bitmask mapping.
        """
        return name in cls.MAPPING

    @classmethod
    def names(cls):
        """
        Return a list of all known content type names. If the ``include_meta``
        flag is set, special purpose content type names will be included in
        the list.
        """
        return cls.MAPPING.keys()

    @classmethod
    def keys(cls, for_type=None):
        """
        Return a dict of key:type mapping that are relevant to the passed in
        content type or for all content types if ``for_type`` is ``None``.
        """
        if for_type:
            return cls.TYPES[for_type]
        # return a set of all content keys collected for all types
        return dict((k, v) for m in cls.TYPES.values() for (k, v) in m.items())

    @classmethod
    def search_keys(cls, for_type=None):
        """
        Return a list of keys that could hold relevant information for text
        based searches on a specific content type, or for all types in case
        ``for_type`` is ``None``.
        """
        if for_type:
            return cls.SEARCH_KEYS[for_type]
        # return a set of all search keys collected for all types
        return set(sum(cls.SEARCH_KEYS.values(), []))
