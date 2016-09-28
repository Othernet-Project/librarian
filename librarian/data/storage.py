"""
zipballs.py: Tools for dealing with zipballs and their sizes

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import hashlib

import pyudev
import hwd.udev
import hwd.storage

from ..core.exts import ext_container as exts


CONSOLIDATE_KEY = 'consolidate_current_id'


def get_storage_id(path):
    md5 = hashlib.md5()
    md5.update(path.encode('utf8'))
    return md5.hexdigest()[:7]


def iterpath(path):
    """
    Start from path, and iterate over the tree bottom-up until root is reached.
    Last item returned is always the root.
    """
    if os.path.islink(path):
        path = os.readlink(path)
    path = os.path.abspath(path)
    while path != '/':
        yield path
        path = os.path.dirname(path)


def find_mount_point(path):
    """
    Return a ``hwd.storage.MtabEntry`` object representing the mount point
    under which the path exists including the path itself if path is the mount
    point.

    For example, if path is /foo/bar and a storage device is mounted under
    /foo/bar, then ``MtabEntry`` for /foo/bar is returned. If a storage device
    is mounted under /foo, then ``MtabEntry`` for /foo is returned, and so on.

    Raises ``ValueError`` if no mount points are found.
    """
    mount_points = {e.mdir: e for e in hwd.storage.mounts()}
    for p in iterpath(path):
        if p in mount_points:
            return mount_points[p]


def get_storage_by_mtab_devname(devname):
    """
    Return a single storage device object for which one of the aliases matches
    device name in mtab. Returns ``None`` if no devices match.
    """
    ctx = pyudev.Context()
    parts = ctx.list_devices(subsystem='block', ID_FS_USAGE='filesystem')
    ubis = ctx.list_devices(subsystem='ubi').match_attribute('alignment', '1')
    devs = map(hwd.storage.Partition, parts) + map(hwd.storage.UbiVolume, ubis)
    for d in devs:
        if devname in d.aliases:
            return d
    return None


def mark_consolidate_started(storage_id):
    exts.cache.set(CONSOLIDATE_KEY, storage_id, timeout=0)


def mark_consolidate_done():
    exts.cache.delete(CONSOLIDATE_KEY)


def get_consolidate_status():
    return exts.cache.get(CONSOLIDATE_KEY)


class StorageError(Exception):
    """ Storage-related errors """
    def __init__(self, storage_id, message):
        self.id = storage_id
        self.message = message
        super(StorageError, self).__init__('<{}> {}'.format(
            storage_id, message))


class NotFoundError(StorageError):
    pass


class NothingToMoveError(StorageError):
    pass


class NoMoveTargetError(StorageError):
    pass


class CapacityError(StorageError):
    def __init__(self, storage_id, capacity, message):
        self.capacity = capacity
        super(CapacityError, self).__init__(storage_id, message)


class StorageDir(object):
    """
    Encapsulates data and methods for a single storage location
    """
    def __init__(self, path):
        self.path = path
        self.id = get_storage_id(self.path)
        self.mount = find_mount_point(path)
        self.stat = os.statvfs(self.path)
        if self.mount:
            self.dev = get_storage_by_mtab_devname(self.mount.dev)
        else:
            self.dev = None

    @property
    def is_loop(self):
        return self.name and self.name.startswith('loop')

    def _try_dev_attr(self, name, default=None):
        if hasattr(self.dev, name):
            return getattr(self.dev, name)
        if hasattr(self.dev.disk, name):
            return getattr(self.dev.disk, name)
        return default

    @property
    def is_removable(self):
        return self._try_dev_attr('is_removable', False)

    @property
    def bus(self):
        return self._try_dev_attr('bus')

    @property
    def humanized_name(self):
        name = self.name
        vendor = self.dev.vendor
        model = self.dev.model
        if self.is_loop:
            name = 'Virtual disk'
        elif vendor or model:
            name = '{} {}'.format(vendor or '', model or '').strip()
        return name

    @property
    def name(self):
        return self.dev.name

    @property
    def total(self):
        return self.stat.f_bsize * self.stat.f_blocks

    @property
    def free(self):
        return self.stat.f_bsize * self.stat.f_bfree

    @property
    def used(self):
        return self.total - self.free

    @property
    def pct_used(self):
        return self.used * 100 / self.total



class Storages(list):

    def __init__(self, paths, ignore_nonexistent=False):
        super(Storages, self).__init__()
        self.lut = {}
        for p in paths:
            s = StorageDir(p)
            if not s.dev:
                if ignore_nonexistent:
                    continue
                raise NotFoundError(s.path, 'No storage device at path')
            self.append(s)
            self.lut[s.id] = s

    def get(self, storage_id):
        if not storage_id:
            raise NotFoundError(None, 'No storage id specified')
        try:
            return self.lut[storage_id]
        except KeyError:
            raise NotFoundError(storage_id, 'No storage device for id')

    def get_all_except(self, storage_id):
        return filter(lambda s: s.id != storage_id, self)

    def test_capacity(self, storage_id):
        target = self.get(storage_id)
        return self.get_total_content_size() < target.free

    def get_total_content_size(self, exclude=[]):
        total = 0
        for s in self:
            if s.id in exclude:
                continue
            total += s.used
        return total

    def move_preflight(self, storage_id):
        dest = self.get(storage_id)
        content_size = self.get_total_content_size(exclude=[storage_id])
        free_space = dest.free
        if not len(self) > 1:
            raise NoMoveTargetError(dest, 'No other drives to move to')
        if not content_size:
            raise NothingToMoveError(dest, 'No content to be moved')
        if free_space < content_size:
            raise CapacityError(dest, content_size,
                                'Not enoguh space on target')
        return dest

    def move_content_to(self, storage_id, pre_start=lambda: True,
                        success_cb=lambda d: True,
                        failure_cb=lambda d: True,
                        partial_cb=lambda d: True):
        try:
            source = self.get(storage_id)
        except NotFoundError:
            failure_cb(None)
        dest_path = source.path
        paths = (s.path for s in self.get_all_except(storage_id))
        pre_start()
        success, is_partial, message = exts.fsal.consolidate(paths, dest_path)
        if success:
            success_cb(source)
        elif is_partial:
            partial_cb(source)
        else:
            failure_cb(source)
        mark_consolidate_done()


def get_content_storages():
    """
    Return a mountable device object matching a storage device used to house
    the content directory.
    """
    success, base_paths = exts.fsal.list_base_paths()
    assert success, 'fsal failed to list base paths'
    return Storages(base_paths, True)
