"""
File system object processors that orchestrate metadata extraction, and provide
additional content type specific helpers.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import itertools
import os

from ...core.exts import ext_container as exts
from . import links
from .contenttypes import ContentTypes
from .metadata import (NO_LANGUAGE,
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

    - py:meth:`get_metadata`: returns a dict with obtained meta information
    - py:class:`deprocess_file`: perform additional cleanup when the metadata
    entry is being deleted
    """
    name = None
    metadata_class = None

    def __init__(self, path, **kwargs):
        if self.name is None:
            raise TypeError("Usage of abstract processor is not allowed."
                            "`name` attribute must be defined.")
        self.path = path
        self.fsal = kwargs.get('fsal', exts.fsal)
        self.keys = ContentTypes.keys(self.name)
        if self.metadata_class:
            self.metadata_extractor = self.metadata_class(self.path, self.fsal)
        else:
            self.metadata_extractor = None

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

    def get_path(self):
        """
        Return the path with which the extracted metadata should be associated.
        Overriding this method allows the implementor to redirect the found
        metadata to another path.
        """
        return self.path

    def process(self, data=None, partial=False):
        """
        Returns either the passed in ``data`` dict if specified, or a new one
        if not, with the extracted meta information from the given ``path``
        merged into it. If the ``partial`` flag is set, only a brief,
        efficiently attainable subset of the information is returned. The
        generated metadata structure is something like:

        {
            '/path/1': {
                'path': '/path/1',
                'type': FILE OR FOLDER,
                'content_types': CONTENT TYPE BITMASK,
                'metadata': {
                    'en': {...},
                    'de': {...},
                }
            },
            '/path/2': {
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
        # check must go against ``None`` to maintain the contract of using the
        # passed in dict
        data = dict() if data is None else data
        new_metadata = self.get_metadata(partial)
        # if metadata is not multilang, wrap it in a dict under ``NO_LANGUAGE``
        # key, otherwise leave it as-is
        if not self.metadata_class or not self.metadata_class.multilang:
            new_metadata = {NO_LANGUAGE: new_metadata}
        # get path with which the metadata should be associated
        path = self.get_path()
        # get existing metadata tree for the current path
        current_data = data.get(path, {})
        # merge extracted metadata with existing metadata, not overwrite it
        existing_metadata = current_data.get('metadata', {})
        self._merge(new_metadata, existing_metadata)
        # update content types
        bitmask = ContentTypes.to_bitmask(self.name)
        content_types = current_data.get('content_types', 0) | bitmask
        # put back updated / merged data
        current_data.update(path=path,
                            content_types=content_types,
                            metadata=existing_metadata)
        if not partial:
            fs_type = (FILE_TYPE, DIRECTORY_TYPE)[self.fsal.isdir(self.path)]
            current_data.update(type=fs_type)
        data[path] = current_data
        return data

    def deprocess(self):
        """
        Called when a facet entry is deleted from the database. Subclasses may
        implement this method if special cleanup is needed.
        """
        pass

    def get_metadata(self, partial):
        """
        It is expected to return a dict object containing the extracted
        metadata from py:attr:`~Processor.path`. The ``partial`` flag indicates
        whether only rudimentary, very quickly attainable information is
        expected to be returned, or to perform a full processing of the target.
        Subclasses may override this method if the default implementation needs
        to be refined for more advanced cases.
        """
        if partial or not self.metadata_extractor:
            # no additional meta information will be available (besides the
            # common data)
            return {}
        # perform full (possibly expensive) processing of metadata
        try:
            meta = self.metadata_extractor.extract()
        except self.metadata_class.MetadataError:
            return {}
        else:
            return dict((k, v) for (k, v) in meta.items() if k in self.keys)

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

    def process(self, data=None, partial=False):
        data = super(HtmlProcessor, self).process(data=data, partial=partial)
        if not partial:
            # assets won't be available for partial processing anyway, and
            # update involves a lot of queries anyway, so skip it
            assets = self.metadata_extractor.assets
            links.update_links(self.path, assets or (), clear=True)
        return data

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
