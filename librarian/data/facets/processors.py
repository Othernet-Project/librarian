import itertools
import os

from ...core.exts import ext_container as exts
from . import links
from .contenttypes import ContentTypes
from .metadata import (runnable,
                       NO_LANGUAGE,
                       ImageMetadata,
                       AudioMetadata,
                       VideoMetadata,
                       HtmlMetadata,
                       DirectoryMetadata)


FILE_TYPE = 0
DIRECTORY_TYPE = 1


def split_name(fname):
    name, ext = os.path.splitext(fname)
    ext = ext[1:].lower()
    return name, ext


def get_extension(fname):
    _, ext = split_name(fname)
    return ext


class ThumbProcessorMixin(object):

    @staticmethod
    def determine_thumb_path(imgpath, thumbdir, extension):
        imgdir = os.path.dirname(imgpath)
        filename = os.path.basename(imgpath)
        (name, _) = os.path.splitext(filename)
        newname = '.'.join([name, extension])
        return os.path.join(imgdir, thumbdir, newname)

    @classmethod
    def create_thumb(cls, srcpath, thumbpath, root, size, quality,
                     callback=None, default=None):
        if os.path.exists(thumbpath):
            return

        thumbdir = os.path.dirname(thumbpath)
        if not os.path.exists(thumbdir):
            os.makedirs(thumbdir)

        (width, height) = map(int, size.split('x'))
        (ret, _) = cls.generate_thumb(srcpath,
                                      thumbpath,
                                      width=width,
                                      height=height,
                                      quality=quality)
        result = os.path.relpath(thumbpath, root) if ret == 0 else default
        if callback:
            callback(srcpath, result)

        return result


class Processor(object):
    """
    Base py:class:`Processor` class. Subclasses are expected to override the
    following attributes:

    - py:attr:`name`: should match the definition from py:class:`ContentTypes`
    - py:attr:`metadata_class`: optional, class which performs extraction of
    metadata

    Methods (optional):

    - py:meth:`get_metadata`: returns a dict with obtained meta information
    - py:class:`deprocess_file`: perform additional cleanup when the metadata
    entry is being deleted
    """
    name = None
    metadata_class = None

    def __init__(self, fsal=None):
        if self.name is None:
            raise TypeError("Usage of abstract processor is not allowed."
                            "`name` attribute must be defined.")
        self.fsal = fsal or exts.fsal
        self.keys = ContentTypes.keys(self.name)

    def _merge(self, source, destination):
        """
        Copy dict of lang:metadata pairs from ``source`` into ``destination``.
        """
        # iterate over ``source``'s lang:meta pairs
        for (language, src_section) in source.items():
            # existing metadata might not have the current language
            dest_section = destination.get(language, {})
            # merge ``language``'s ``src_section`` into ``dest_section``
            dest_section.update(src_section)
            # put back (or insert) merged ``dest_section`` that was just
            # updated with ``src_section`` into ``desctination``
            destination[language] = dest_section

    def process_file(self, path, data=None, partial=False):
        """
        Returns either the passed in ``data`` dict if specified, or a new one
        if not, with the extracted meta information from the given ``path``
        merged into it. If the ``partial`` flag is set, only a brief,
        efficiently attainable subset of the information is returned.
        """
        # check must go against ``None`` to maintain the contract of using the
        # passed in dict
        data = dict() if data is None else data
        new_metadata = self.get_metadata(path, partial)
        # if metadata is not multilang, wrap it in a dict under ``NO_LANGUAGE``
        # key, otherwise leave it as-is
        if not self.metadata_class or not self.metadata_class.multilang:
            new_metadata = {NO_LANGUAGE: new_metadata}
        # merge with existing metadata, not overwrite it
        existing_metadata = data.get('metadata', {})
        self._merge(new_metadata, existing_metadata)
        bitmask = ContentTypes.to_bitmask(self.name)
        data.update(path=path,
                    content_types=data.get('content_types', 0) | bitmask,
                    metadata=existing_metadata)
        if not partial:
            fs_type = DIRECTORY_TYPE if self.fsal.isdir(path) else FILE_TYPE
            data.update(type=fs_type)
        return data

    def deprocess_file(self, path):
        """
        Called when a facet entry is deleted from the database. Subclasses may
        implement this method if special cleanup is needed.
        """
        pass

    def get_metadata(self, path, partial):
        """
        It is expected to return a dict object containing the attained metadata
        from ``path``. The ``partial`` flag indicates whether only rudimentary,
        very quickly attainable information is expected to be returned, or to
        perform a full processing of the target.
        Subclasses may override this method if the default implementation needs
        to be refined for more advanced cases.
        """
        if partial or not self.metadata_class:
            # no additional meta information will be available (besides the
            # common data)
            return {}
        # perform full (possibly expensive) processing of metadata
        try:
            meta = self.metadata_class(self.fsal, path)
        except IOError:
            return {}
        else:
            return dict((k, getattr(meta, k)) for k in self.keys)

    @classmethod
    def is_entry_point(cls, new, old=None):
        """
        Processors handling types of more complex structure can elect a main
        file which serves as a default entry point when opening a folder with
        a specific facet. Returning ``True`` will tell the caller that the
        passed in ``path`` can be used as the entry point. ``new`` should be
        the path to the new candidate for election, and ``old`` should be the
        existing one, which could affect the decision.
        """
        return False

    @classmethod
    def can_process(cls, path):
        """
        Return whether the processor can handle a given ``path``.
        """
        return get_extension(path) in cls.EXTENSIONS

    @classmethod
    def for_path(cls, path):
        """
        Return all the applicable processors for a given ``path``.
        """
        processors = [proc_cls for proc_cls in cls.subclasses()
                      if proc_cls.can_process(path)]
        if not processors:
            raise RuntimeError("No processor found for the given path.")
        return processors

    @classmethod
    def for_type(cls, content_type):
        """
        Return all the applicable processors for a given ``content_type``.
        """
        for proc_cls in cls.subclasses():
            if proc_cls.name == content_type:
                return proc_cls
        raise RuntimeError("No processor found for the given content type.")

    @classmethod
    def subclasses(cls, source=None):
        """
        Return all the subclasses of ``cls``.
        """
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.subclasses(source=child))
        return result


class GenericFacetProcessor(Processor):
    name = ContentTypes.GENERIC

    @classmethod
    def can_process(cls, path):
        return True


class HtmlFacetProcessor(Processor):
    name = ContentTypes.HTML
    metadata_class = HtmlMetadata

    EXTENSIONS = ['html', 'htm', 'xhtml']
    INDEX_NAMES = ['index', 'main', 'start']
    FILE_NAMES = list(reversed(['.'.join(p)
                                for p in itertools.product(INDEX_NAMES,
                                                           EXTENSIONS)]))

    @classmethod
    def _score(cls, filename):
        """
        Return the passed in ``filename``'s position in the candidate list or
        ``-1`` if it's not in there.
        """
        try:
            return cls.FILE_NAMES.index(filename)
        except ValueError:
            return -1

    @classmethod
    def is_entry_point(cls, new, old=None):
        """
        Return ``True`` if ``new`` path is a better candidate for being the
        index file, or ``False`` if it isn't. Filenames are scored based on
        their position in the list. The higher the score, the better the
        candidate is."""
        # get filenames of passed in paths
        old_name = os.path.basename(old) if old else None
        new_name = os.path.basename(new) if new else None
        return cls._score(old_name) < cls._score(new_name)

    def process_file(self, path, data=None, partial=False):
        data = super(HtmlFacetProcessor, self).process_file(path,
                                                            data=data,
                                                            partial=partial)
        if not partial:
            # assets won't be available for partial processing anyway, and
            # update involves a lot of queries anyway, so skip it
            assets = data.pop('assets', None)
            links.update_links(path, assets or (), clear=True)
        return data

    def deprocess_file(self, path):
        links.remove_links(path)

    def get_metadata(self, path, partial):
        if partial:
            return {}
        try:
            meta = self.metadata_class(self.fsal, path)
        except IOError:
            return {}
        else:
            data = dict((k, getattr(meta, k)) for k in self.keys)
            # `assets` will be popped out before passing it back to the caller
            data['assets'] = meta.assets
            return data


class ImageFacetProcessor(Processor, ThumbProcessorMixin):
    name = ContentTypes.IMAGE
    metadata_class = ImageMetadata

    EXTENSIONS = ['jpg', 'jpeg', 'png']

    @staticmethod
    @runnable()
    def generate_thumb(src, dest, width, height, quality, **kwargs):
        return [
            "ffmpeg",
            "-i",
            src,
            "-q:v",
            str(quality),
            "-vf",
            "scale='if(gt(in_w,in_h),-1,{height})':'if(gt(in_w,in_h),{width},-1)',crop={width}:{height}".format(width=width, height=height),  # NOQA
            dest
        ]


class AudioFacetProcessor(Processor, ThumbProcessorMixin):
    name = ContentTypes.AUDIO
    metadata_class = AudioMetadata

    EXTENSIONS = ['mp3', 'wav', 'ogg']

    @staticmethod
    @runnable()
    def generate_thumb(src, dest, **kwargs):
        return [
            "ffmpeg",
            "-i",
            src,
            "-an",
            "-vcodec",
            "copy",
            dest
        ]


class VideoFacetProcessor(Processor, ThumbProcessorMixin):
    name = ContentTypes.VIDEO
    metadata_class = VideoMetadata

    EXTENSIONS = ['mp4', 'wmv', 'webm', 'flv', 'ogv']

    @staticmethod
    @runnable()
    def generate_thumb(src, dest, skip_secs=3, **kwargs):
        return [
            "ffmpeg",
            "-ss",
            str(skip_secs),
            "-i",
            src,
            "-vf",
            "select=gt(scene\,0.5)",
            "-frames:v",
            "1",
            "-vsync",
            "vfr",
            dest
        ]


class DirectoryProcessor(Processor):
    name = ContentTypes.DIRECTORY
    metadata_class = DirectoryMetadata

    DIRINFO_FILENAME = '.dirinfo'

    @classmethod
    def can_process(cls, path):
        return os.path.basename(path) == cls.DIRINFO_FILENAME

    def process_file(self, *args, **kwargs):
        data = super(DirectoryProcessor, self).process_file(*args, **kwargs)
        # for each passed in dirinfo file, the data should be associated with
        # the path of the directory itself, not the dirinfo file
        dirpath = os.path.dirname(data['path'])
        data.update(path=dirpath)
        return data

    def get_metadata(self, path, partial):
        if partial:
            return {}
        try:
            meta = self.metadata_class(self.fsal, path)
        except IOError:
            return {}
        else:
            return meta.data
