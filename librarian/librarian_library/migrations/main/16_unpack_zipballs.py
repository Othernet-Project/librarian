import errno
import os
import re
import shutil
import zipfile

import scandir


COMP_RE = re.compile(r'([0-9a-f]{2,3})')
SQL = 'update zipballs set size = ? where md5 = ?;'
DISABLE_SQL = 'update zipballs set disabled = 1 where md5 = ?;'


def get_hash(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def unpack_zipball(md5, zip_path, content_dir):
    path_components = COMP_RE.findall(md5)
    content_src = os.path.join(content_dir, md5)
    content_dest = os.path.join(content_dir, *path_components)
    # make sure previous folder does not exists from a previous possibly
    # failed migratio
    if os.path.exists(content_dest):
        shutil.rmtree(content_dest)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(content_dir)
    except IOError as exc:
        if exc.errno == errno.ENOSPC:
            # no space left on drive, do not try unpacking other zipballs
            return False
        raise
    else:
        # move folder contents to new content path (ignore top level dir)
        shutil.move(content_src, content_dest)
        # remove zip file
        os.remove(zip_path)
        return True
    finally:
        # cleanup if needed
        if os.path.exists(content_src):
            shutil.rmtree(content_src)


def up(db, conf):
    content_dir = conf['library.contentdir']
    for entry in scandir.scandir(content_dir):
        if entry.name.endswith('.zip'):
            md5 = get_hash(entry.name)
            size = entry.stat().st_size
            is_unpacked = unpack_zipball(md5, entry.path, content_dir)
            if is_unpacked:
                db.execute(SQL, (size, md5))
            else:
                db.execute(DISABLE_SQL, (md5,))
