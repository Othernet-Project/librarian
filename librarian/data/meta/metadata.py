from __future__ import unicode_literals

import itertools
import json
import logging
import os
import re
import urlparse

from bottle_utils.common import to_unicode
from bs4 import BeautifulSoup

from .utils import run_command


FFPROBE_CMD = 'ffprobe -v quiet -i HOLDER1 -show_entries HOLDER2 -print_format json'
NO_LANGUAGE = ''


def build_ffprobe_command(path, entries=('format', 'streams')):
    show_entries = ':'.join(entries)
    command = FFPROBE_CMD.split(' ')
    command[4] = path
    command[6] = show_entries
    return command


def find_in_dicts(dicts, tags):
    for d in dicts:
        for tag in tags:
            if tag in d:
                return d[tag]


class BaseMetadata(object):
    #: Determines whether the returned metadata is available in multiple
    #: languages or not
    multilang = False

    def __init__(self, fsal, path):
        self.fsal = fsal
        self.path = to_unicode(path)


class FFmpegMetadataWrapper(BaseMetadata):

    ENTRIES = ('format', 'streams')

    def __init__(self, *args, **kwargs):
        entries = kwargs.pop('entries', self.ENTRIES)
        super(FFmpegMetadataWrapper, self).__init__(*args, **kwargs)

        success, fso = self.fsal.get_fso(self.path)
        if not success:
            msg = u'Error while extracting metadata: No such file: {}'.format(
                self.path)
            logging.error(msg)
            raise IOError(msg)
        command = build_ffprobe_command(fso.path, entries=entries)
        (ret, output) = run_command(command, timeout=5)
        if not output:
            msg = u'Error extracting metadata: Extraction timedout or failed'
            raise IOError(msg)
        try:
            self.data = json.loads(output)
        except ValueError:
            msg = u'Error extracting metadata: JSON expected, got {}'.format(
                type(output))
            raise IOError(msg)

    def get_duration(self):
        fmt = self.data.get('format', dict())
        if 'duration' in fmt:
            return float(fmt['duration'])
        streams = self.data.get('streams', list())
        duration = 0
        for stream in streams:
            if 'duration' in stream:
                s_duration = float(stream['duration'])
                if duration < s_duration:
                    duration = s_duration
        return duration

    def get_format_tag(self, tags, default=''):
        fmt = self.data.get('format', dict())
        format_tags = fmt.get('tags', dict())
        for tag in tags:
            if tag in format_tags:
                return format_tags[tag]
        return default


class FFmpegImageMetadata(FFmpegMetadataWrapper):

    ENTRIES = ('frames',)

    def __init__(self, *args, **kwargs):
        kwargs['entries'] = self.ENTRIES
        super(FFmpegImageMetadata, self).__init__(*args, **kwargs)

        self.width, self.height = self.get_dimensions()
        self.title = self.get_frames_tag(('title', 'ImageDescription'))

    def get_dimensions(self):
        width = self.get_frames_tag(('width',), 0)
        height = self.get_frames_tag(('height',), 0)
        return width, height

    def get_frames_tag(self, tags, default=''):
        frames = self.data.get('frames', [])
        for frame in frames:
            frame_tags = frame.get('tags', dict())
            search_space = (frame, frame_tags)
            ret = find_in_dicts(search_space, tags)
            if ret is not None:
                return ret
        return default


class FFmpegAudioVideoMetadata(FFmpegMetadataWrapper):

    def __init__(self, *args, **kwargs):
        super(FFmpegAudioVideoMetadata, self).__init__(*args, **kwargs)
        self.width, self.height = self.get_dimensions()
        self.duration = self.get_duration()
        self.title = self.get_format_tag(('title',))
        self.author = self.get_format_tag(('author', 'artist'))
        self.description = self.get_format_tag(('description', 'comment'))

    def get_dimensions(self):
        streams = self.data.get('streams', list())
        width, height = (0, 0)
        for stream in streams:
            width = stream.get('width', width)
            height = stream.get('height', height)
        return width, height


class AudioMetadata(FFmpegAudioVideoMetadata):

    def __init__(self, *args, **kwargs):
        super(AudioMetadata, self).__init__(*args, **kwargs)
        self.genre = self.get_format_tag(('genre',))
        self.album = self.get_format_tag(('album',))


def get_tag_attr(tags, attr):
    return (tag[attr] for tag in tags if attr in tag.attrs)


def get_local_path(dirpath, url):
    result = urlparse.urlparse(url)
    is_local = result.scheme == ''
    if is_local:
        path = os.path.normpath(os.path.join(dirpath, url))
    else:
        path = None
    return is_local, path


class HtmlMetadata(BaseMetadata):
    PARSER = 'html.parser'

    def __init__(self, *args, **kwargs):
        super(HtmlMetadata, self).__init__(*args, **kwargs)
        success, fso = self.fsal.get_fso(self.path)
        if not success:
            msg = u'Error while extracting metadata: No such file: {}'.format(
                self.path)
            logging.error(msg)
            raise IOError(msg)

        self.data = {}
        with open(fso.path, 'r') as f:
            dom = BeautifulSoup(f, self.PARSER)
            for meta in dom.find_all('meta'):
                if 'name' in meta.attrs:
                    key = meta.attrs['name']
                    value = meta.attrs['content']
                    self.data[key] = value
                # Old style html files may have the language set via
                # <meta http-equiv="content-language">
                pragma = meta.get('http-equiv', '').lower()
                if pragma == 'content-language':
                    self.data['language'] = meta.get('content')
            if dom.html:
                lang = dom.html.get('lang') or self.data.get('language', '')
                self.data['language'] = lang
            if dom.title:
                self.data['title'] = dom.title.string
            is_formatting_on = self.data.get('outernet_formatting') == 'true'
            self.data['outernet_formatting'] = is_formatting_on
            self.data['assets'] = self.extract_asset_paths(dom)
            dom.decompose()

    def __getattr__(self, name):
        return self.data.get(name, '')

    def extract_asset_paths(self, dom):
        assets = []
        links = (
            get_tag_attr(dom.find_all('link'), 'href'),
            get_tag_attr(dom.find_all('script'), 'src'),
            get_tag_attr(dom.find_all('img'), 'src'),
            get_tag_attr(dom.find_all('a'), 'href'),
        )
        dirpath = os.path.dirname(self.path)
        for url in itertools.chain(*links):
            is_local, path = get_local_path(dirpath, url)
            if is_local:
                assets.append(path)
        return assets

ImageMetadata = FFmpegImageMetadata


VideoMetadata = FFmpegAudioVideoMetadata


class DirectoryMetadata(BaseMetadata):
    multilang = True

    SPLITTER = '='
    ENTRY_REGEX = re.compile(r'(\w+)\[(\w+)\]')

    def __init__(self, *args, **kwargs):
        super(DirectoryMetadata, self).__init__(*args, **kwargs)
        self.data = dict()
        # read and convert to unicode all lines
        with self.fsal.open(self.path, 'r') as dirinfo_file:
            raw = [to_unicode(line) for line in dirinfo_file.readlines()]
        # unpack each line
        for line in raw:
            (key, value) = line.split(self.SPLITTER)
            match = self.ENTRY_REGEX.match(key)
            if match:
                (key, language) = match.groups()
            else:
                language = NO_LANGUAGE
            self.data.setdefault(language, {})
            self.data[language][key] = value.strip()
