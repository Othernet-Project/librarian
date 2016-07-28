"""
Tools for extracting metadata from file system objects.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
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


NO_LANGUAGE = ''


class MetadataError(Exception):
    """
    Exception raised when metadata cannot be extracted for some reason.
    """
    pass


class BaseMetadata(object):
    """
    Metadata extractors should inherit from this base class.
    """
    #: Determines whether the returned metadata is available in multiple
    #: languages or not
    multilang = False
    #: Exception classes
    MetadataError = MetadataError

    def __init__(self, path, fsal):
        self.path = to_unicode(path)
        self.fsal = fsal

    def extract(self):
        raise NotImplementedError()


class FFmpegMetadata(BaseMetadata):
    ENTRIES = ('format', 'streams')
    FFPROBE_CMD = 'ffprobe -v quiet -i {} -show_entries {} -print_format json'

    @classmethod
    def build_ffprobe_command(cls, path, entries):
        show_entries = ':'.join(entries)
        command = cls.FFPROBE_CMD.split(' ')
        command[4] = path
        command[6] = show_entries
        return command

    def probe(self):
        (success, fso) = self.fsal.get_fso(self.path)
        if not success:
            msg = (u'Metadata extraction failed, file not found: '
                   u'{}'.format(self.path))
            logging.error(msg)
            raise self.MetadataError(msg)
        command = self.build_ffprobe_command(fso.path, entries=self.ENTRIES)
        (_, output) = run_command(command, timeout=5)
        if not output:
            msg = u'Metadata extraction timed out or failed.'
            raise self.MetadataError(msg)
        try:
            return json.loads(output)
        except ValueError as exc:
            msg = u'Metadata parsing failed: {}'.format(exc)
            raise self.MetadataError(msg)


class FFmpegImageMetadata(FFmpegMetadata):
    ENTRIES = ('frames',)

    def extract(self):
        raw_data = self.probe()
        title = self.get_frames_tag(raw_data, ('title', 'ImageDescription'))
        width = self.get_frames_tag(raw_data, ('width',), 0)
        height = self.get_frames_tag(raw_data, ('height',), 0)
        return dict(title=title, width=width, height=height)

    @staticmethod
    def get_frames_tag(data, tags, default=''):
        frames = data.get('frames', [])
        for frame in frames:
            frame_tags = frame.get('tags', dict())
            for tag in tags:
                if tag in frame:
                    return frame[tag]
                if tag in frame_tags:
                    return frame_tags[tag]
        return default


class FFmpegAudioVideoMetadata(FFmpegMetadata):
    tags = (
        ('title', ['title']),
        ('author', ['author', 'artist']),
        ('description', ['description', 'comment']),
    )

    def extract(self):
        raw_data = self.probe()
        duration = self.get_duration(raw_data)
        (width, height) = self.get_dimensions(raw_data)
        data = dict((key, self.get_format_tag(raw_data, tags))
                    for (key, tags) in self.tags)
        data.update(duration=duration,
                    width=width,
                    height=height)
        return data

    @staticmethod
    def get_format_tag(data, tags, default=''):
        fmt = data.get('format', dict())
        format_tags = fmt.get('tags', dict())
        for tag in tags:
            if tag in format_tags:
                return format_tags[tag]
        return default

    @staticmethod
    def get_duration(data):
        fmt = data.get('format', dict())
        if 'duration' in fmt:
            return float(fmt['duration'])
        streams = data.get('streams', list())
        duration = 0.0
        for stream in streams:
            if 'duration' in stream:
                s_duration = float(stream['duration'])
                if duration < s_duration:
                    duration = s_duration
        return duration

    @staticmethod
    def get_dimensions(data):
        streams = data.get('streams', list())
        (width, height) = (0, 0)
        for stream in streams:
            width = stream.get('width', width)
            height = stream.get('height', height)
        return (width, height)


class AudioMetadata(FFmpegAudioVideoMetadata):
    tags = FFmpegAudioVideoMetadata.tags + (
        ('genre', ['genre']),
        ('album', ['album']),
    )


VideoMetadata = FFmpegAudioVideoMetadata
ImageMetadata = FFmpegImageMetadata


class HtmlMetadata(BaseMetadata):
    PARSER = 'html.parser'

    def extract(self):
        self.assets = None
        try:
            with self.fsal.open(self.path, 'r') as html_file:
                dom = BeautifulSoup(html_file, self.PARSER)
        except Exception:
            msg = (u"Metadata extraction failed, error opening: "
                   u"{}".format(self.path))
            logging.exception(msg)
            raise self.MetadataError(msg)
        else:
            data = {}
            for meta in dom.find_all('meta'):
                if all(key in meta.attrs for key in ('name', 'content')):
                    key = meta.attrs['name']
                    value = meta.attrs['content']
                    data[key] = value
                # Old style html files may have the language set via
                # <meta http-equiv="content-language">
                pragma = meta.get('http-equiv', '').lower()
                if pragma == 'content-language':
                    data['language'] = meta.get('content')
            if dom.html:
                lang = dom.html.get('lang') or data.get('language', '')
                data['language'] = lang
            if dom.title:
                data['title'] = dom.title.string
            is_formatting_on = data.get('outernet_formatting') == 'true'
            data['outernet_formatting'] = is_formatting_on
            # assets are not directly part of the metadata, but are needed
            # to be accessed from within the processor, so it's kept as an
            # instance attribute only
            self.assets = self.extract_asset_paths(dom)
            dom.decompose()
            return data

    @staticmethod
    def get_tag_attr(tags, attr):
        return (tag[attr] for tag in tags if attr in tag.attrs)

    @staticmethod
    def get_local_path(dirpath, url):
        result = urlparse.urlparse(url)
        is_local = result.scheme == ''
        if is_local:
            path = os.path.normpath(os.path.join(dirpath, url))
        else:
            path = None
        return is_local, path

    def extract_asset_paths(self, dom):
        assets = []
        links = (
            self.get_tag_attr(dom.find_all('link'), 'href'),
            self.get_tag_attr(dom.find_all('script'), 'src'),
            self.get_tag_attr(dom.find_all('img'), 'src'),
            self.get_tag_attr(dom.find_all('a'), 'href'),
        )
        dirpath = os.path.dirname(self.path)
        for url in itertools.chain(*links):
            is_local, path = self.get_local_path(dirpath, url)
            if is_local:
                assets.append(path)
        return assets


class DirectoryMetadata(BaseMetadata):
    multilang = True

    SPLITTER = '='
    ENTRY_REGEX = re.compile(r'(\w+)\[(\w+)\]')
    DEFAULT_COVER = 'cover.jpg'

    def _add_default_cover(self, data):
        # add default cover image filename under ``cover`` key if it exists
        folder_path = os.path.dirname(self.path)
        cover_path = os.path.join(folder_path, self.DEFAULT_COVER)
        if self.fsal.exists(cover_path):
            # the path of the cover should be relative to the folder where it's
            # contained
            data[NO_LANGUAGE]['cover'] = self.DEFAULT_COVER

    def extract(self):
        data = dict()
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
            data.setdefault(language, {})
            data[language][key] = value.strip()
        # if there is no folder cover image under the language-less version of
        # the metadata, check for the default cover and add if available
        if not data[NO_LANGUAGE].get('cover'):
            self._add_default_cover(data)

        return data
