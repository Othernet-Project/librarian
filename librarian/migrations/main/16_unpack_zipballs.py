import errno
import os
import re
import shutil
import tempfile
import zipfile

import scandir


COMP_RE = re.compile(r'([0-9a-f]{2,3})')
SQL = 'update zipballs set size = ? where md5 = ?;'


def unpack_zipball(zip_path, content_dir):
    filename = os.path.basename(zip_path)
    (md5, _) = os.path.splitext(filename)
    path_components = COMP_RE.findall(md5)
    content_dest = os.path.join(content_dir, *path_components)
    # make sure previous folder does not exists from a previous possibly
    # failed migratio
    if os.path.exists(content_dest):
        shutil.rmtree(content_dest)

    try:
        # extract zip to a temporary location
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(tmp_dir)
    except IOError as exc:
        if exc.errno == errno.ENOSPC:
            # no space left on drive, do not try unpacking other zipballs
            return None
        raise
    else:
        # move folder contents to new content path (ignore top level dir)
        content_src = os.path.join(tmp_dir, md5)
        shutil.move(content_src, content_dest)
        # remove zip file
        os.remove(zip_path)
        return md5
    finally:
        # remove tmp folder
        shutil.rmtree(tmp_dir)


def up(db, conf):
    content_dir = conf['content.contentdir']
    for entry in scandir.scandir(content_dir):
        if entry.name.endswith('.zip'):
            size = entry.stat().st_size
            md5 = unpack_zipball(entry.path, content_dir)
            if md5 is not None:
                db.execute(SQL, (size, md5))
