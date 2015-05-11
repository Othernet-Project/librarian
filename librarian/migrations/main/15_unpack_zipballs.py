import os
import re
import shutil
import tempfile
import zipfile

import scandir


COMP_RE = re.compile(r'([0-9a-f]{2,3})')


def up(db, conf):
    content_dir = conf['content.contentdir']
    zip_paths = (zfile.path for zfile in scandir.scandir(content_dir)
                 if zfile.name.endswith('.zip'))
    for zip_path in zip_paths:
        filename = os.path.basename(zip_path)
        (md5, _) = os.path.splitext(filename)
        path_components = COMP_RE.findall(md5)
        content_dest = os.path.join(content_dir, *path_components)
        # make sure previous folder does not exists from a previous possibly
        # failed migratio
        if os.path.exists(content_dest):
            shutil.rmtree(content_dest)

        # extract zip to a temporary location
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(tmp_dir)

        # move folder contents to new content path (ignore top level dir)
        content_src = os.path.join(tmp_dir, md5)
        shutil.move(content_src, content_dest)
        # remove tmp folder
        shutil.rmtree(tmp_dir)
        # remove zip file
        os.remove(zip_path)
