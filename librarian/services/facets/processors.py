import os

from librarian_core.exts import ext_container as exts

import links
from .facets import FACET_TYPES
from .metadata import (runnable, ImageMetadata, AudioMetadata,
                       VideoMetadata, HtmlMetadata)


IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']


def split_name(fname):
    name, ext = os.path.splitext(fname)
    ext = ext[1:].lower()
    return name, ext


def get_extension(fname):
    _, ext = split_name(fname)
    return ext


def strip_extension(fname):
    name, _ = split_name(fname)
    return name


def is_html_file(ext):
    return ext in HtmlFacetProcessor.EXTENSIONS


def get_facet_processors(path):
    all_processors = FacetProcessorBase.subclasses()
    valid_processors = [p() for p in all_processors if p.can_process(path)]
    return valid_processors


class FacetProcessorBase(object):
    name = None

    def __init__(self):
        if self.name is None:
            raise TypeError("Usage of abstract processor is not allowed."
                            "`name` attribute must be defined.")
        self.fsal = exts.fsal

    def process_file(self, facets, path, partial=False):
        meta = self._get_metadata(path, partial)
        facets.update(meta)
        facets['facet_types'] |= FACET_TYPES[self.name]
        return True

    def deprocess_file(self, facets, path):
        pass

    def _get_metadata(self, path, partial):
        raise NotImplemented()

    @classmethod
    def can_process(cls, path):
        if hasattr(cls, 'EXTENSIONS'):
            extensions = list(getattr(cls, 'EXTENSIONS'))
            return get_extension(path) in extensions
        return False

    @classmethod
    def get_processors(cls, path):
        processors = []
        for processor_cls in cls.subclasses():
            if processor_cls.can_process(path):
                processors.append(processor_cls)
        if processors:
            return processors
        else:
            raise RuntimeError("No processor found for the given type.")

    @classmethod
    def subclasses(cls, source=None):
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.subclasses(source=child))
        return result

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


class GenericFacetProcessor(FacetProcessorBase):
    name = 'generic'

    def _get_metadata(self, *args, **kwargs):
        return {}

    @classmethod
    def can_process(cls, path):
        return True


class HtmlFacetProcessor(FacetProcessorBase):
    name = 'html'

    EXTENSIONS = ['html', 'htm', 'xhtml']

    INDEX_NAMES = ['index', 'main', 'start']

    def process_file(self, facets, path, partial=False):
        meta, assets = self._get_metadata(path, partial)
        facets.update(meta)
        facets['facet_types'] |= FACET_TYPES[self.name]

        links.update_links(path, assets or (), clear=True)
        return True

    def deprocess_file(self, facets, path):
        links.remove_links(path)

    def _get_metadata(self, path, partial):
        if partial:
            return {}, None
        try:
            meta = HtmlMetadata(self.fsal, path)
            keys = ('author', 'title', 'description', 'keywords',
                    'language', 'copyright')
            data = {}
            for key in keys:
                data[key] = getattr(meta, key)
            data['outernet_formatting'] = (meta.outernet_formatting == 'true')
            return data, meta.assets
        except IOError:
            return {}, None


class ImageFacetProcessor(FacetProcessorBase):
    name = 'image'

    EXTENSIONS = IMAGE_EXTENSIONS

    def _get_metadata(self, path, partial):
        if partial:
            return {}
        try:
            meta = ImageMetadata(self.fsal, path)
            return {
                'title': meta.title,
                'width': meta.width,
                'height': meta.height
            }
        except IOError:
            return {}

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


class AudioFacetProcessor(FacetProcessorBase):
    name = 'audio'

    EXTENSIONS = ['mp3', 'wav', 'ogg']

    def _get_metadata(self, path, partial):
        if partial:
            return {}
        try:
            meta = AudioMetadata(self.fsal, path)
            return {
                'author': meta.author,
                'title': meta.title,
                'album': meta.album,
                'genre': meta.genre,
                'duration': meta.duration
            }
        except IOError:
            return {}

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


class VideoFacetProcessor(FacetProcessorBase):
    name = 'video'

    EXTENSIONS = ['mp4', 'wmv', 'webm', 'flv', 'ogv']

    def _get_metadata(self, path, partial):
        if partial:
            return {}
        try:
            meta = VideoMetadata(self.fsal, path)
            return {
                'title': meta.title,
                'author': meta.author,
                'description': meta.description,
                'width': meta.width,
                'height': meta.height,
                'duration': meta.duration,
            }
        except IOError:
            return {}

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
