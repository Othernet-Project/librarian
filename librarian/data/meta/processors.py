"""
File system object processors that orchestrate metadata extraction, and provide
additional content type specific helpers.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import itertools
import mimetypes
import os

from ...core.exts import ext_container as exts
from . import links
from .contenttypes import ContentTypes
from .metadata import (NO_LANGUAGE,
                       MetadataError,
                       ImageMetadata,
                       AudioMetadata,
                       VideoMetadata,
                       HtmlMetadata,
                       DirectoryMetadata)
from .utils import runnable


FILE_TYPE = 0
DIRECTORY_TYPE = 1


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

    - py:meth:`~Processor.get_metadata`: returns a dict with obtained metadata
    - py:meth:`~Processor.deprocess`: perform additional cleanup when metadata
    is being deleted
    """
    _subclasses = ()
    name = None
    metadata_class = None

    def __init__(self, path, **kwargs):
        if self.name is None:
            raise TypeError("Usage of abstract processor is not allowed."
                            "`name` attribute must be defined.")
        self.path = path
        self.partial = kwargs.get('partial', False)
        # container into which metadata will be put
        self.data = kwargs.get('data', {})
        self.fsal = kwargs.get('fsal', exts.fsal)
        self.keys = ContentTypes.keys(self.name)
        if self.metadata_class:
            self.metadata_extractor = self.metadata_class(self.path, self.fsal)
        else:
            self.metadata_extractor = None

    @staticmethod
    def _merge(source, destination):
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

    def get_path(self):
        """
        Return the path with which the extracted metadata should be associated.
        Overriding this method allows the implementor to redirect the found
        metadata to another path.
        """
        return self.path

    def get_metadata(self):
        """
        Return a dict object containing the extracted metadata from
        py:attr:`~Processor.path`. If the py:attr:`~Processor.partial`` flag
        is set, or no py:attr:`~Processor.metadata_class` was specified, no
        metadata extraction will happen.
        """
        if self.partial or not self.metadata_extractor:
            # no additional meta information will be available (besides the
            # common data)
            return {}
        # perform full (possibly expensive) processing of metadata
        try:
            meta = self.metadata_extractor.extract()
        except MetadataError:
            return {}
        else:
            return dict((k, v) for (k, v) in meta.items() if k in self.keys)

    def _add_metadata(self, dest):
        """
        Get metadata and merge it into ``dest``.
        """
        new_metadata = self.get_metadata()
        # if metadata is not multilang, wrap it in a dict under ``NO_LANGUAGE``
        # key, otherwise leave it as-is
        if not self.metadata_class or not self.metadata_class.multilang:
            new_metadata = {NO_LANGUAGE: new_metadata}
        # merge extracted metadata with existing metadata, not overwrite it
        existing_metadata = dest.get('metadata', {})
        self._merge(new_metadata, existing_metadata)
        dest['metadata'] = existing_metadata

    def _add_fs_data(self, dest):
        """
        Add generic information that can be gathered without metadata
        extraction to ``dest``.
        """
        # update content types
        bitmask = ContentTypes.to_bitmask(self.name)
        content_types = dest.get('content_types', 0) | bitmask
        # put back updated / merged data

        (mime_type, _) = mimetypes.guess_type(self.path)
        dest.update(path=self.get_path(),
                    mime_type=mime_type,
                    content_types=content_types)
        # because it is an expensive operation, it is performed only in for
        # non-partial requests.
        if not self.partial:
            # the check should be performed against the original path, not the
            # path of meta redirection
            fs_type = (FILE_TYPE, DIRECTORY_TYPE)[self.fsal.isdir(self.path)]
            dest.update(type=fs_type)

    def process(self):
        """
        Process the file system object specified by py:attr:`~Processor.path`.
        If py:attr:`~Processor.partial` is set, only generic, efficiently
        obtainable information will be put into py:attr:`~Processor.data`.
        In case py:attr:`~Processor.partial` is not set, metadata extraction
        will take place and will be put into py:attr:`~Processor.data`.
        By overriding py:meth:`~Processor.get_path`, it is possible for a
        processor to point the extracted metadata at a different path.
        A possible structure of py:attr:`~Processor.data` after full metadata
        extraction would look like:

            {
                '/path/original': {
                    'path': '/path/1',
                    'type': FILE OR FOLDER,
                    'content_types': CONTENT TYPE BITMASK,
                    'metadata': {
                        'en': {...},
                        'de': {...},
                    }
                },
                '/path/redirected/if/any': {
                    'path': '/path/2',
                    'type': FILE OR FOLDER,
                    'content_types': CONTENT TYPE BITMASK,
                    'metadata': {
                        'en': {...},
                        'de': {...},
                    }
                }
            }
        """
        # get path to which the found metadata should be connected
        path = self.get_path()
        # get existing metadata structure for either the original path or the
        # path to which the metadata is being redirected
        data_for_path = self.data.get(path, {})
        # add generic data related to file system objects generally
        self._add_fs_data(data_for_path)
        # add extracted metadata
        self._add_metadata(data_for_path)
        # put back updated or newly created structure
        self.data[path] = data_for_path

    def deprocess(self):
        """
        Called when a meta entry is deleted from the database. Subclasses may
        implement this method if special cleanup is needed.
        """
        pass

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
        (_, ext) = os.path.splitext(path)
        ext = ext[1:].lower()
        return ext in cls.EXTENSIONS

    @classmethod
    def for_path(cls, path):
        """
        Return all the applicable processors for a given ``path``.
        """
        cls._subclasses = cls._subclasses or cls.subclasses()
        return (proc_cls for proc_cls in cls._subclasses
                if proc_cls.can_process(path))

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


class GenericProcessor(Processor):
    name = ContentTypes.GENERIC

    @classmethod
    def can_process(cls, path):
        return True


class HtmlProcessor(Processor):
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

    def process(self):
        super(HtmlProcessor, self).process()
        if not self.partial:
            # assets won't be available for partial processing anyway, and
            # update involves a lot of queries, so skip it
            assets = self.metadata_extractor.assets
            links.update_links(self.path, assets or (), clear=True)

    def deprocess(self):
        links.remove_links(self.path)


class ImageProcessor(Processor, ThumbProcessorMixin):
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


class AudioProcessor(Processor, ThumbProcessorMixin):
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


class VideoProcessor(Processor, ThumbProcessorMixin):
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

    def get_path(self):
        # for each passed in dirinfo file, the data should be associated with
        # the path of the directory itself, not the dirinfo file
        return os.path.dirname(self.path)
