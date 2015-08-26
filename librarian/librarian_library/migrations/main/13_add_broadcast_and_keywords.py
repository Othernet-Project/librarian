import json
import os
import zipfile

import dateutil.parser


SQL = """
alter table zipballs add column broadcast date;
alter table zipballs add column keywords varchar not null default '';
"""
DATA_SQL = "update zipballs set broadcast = ? where md5 = ?;"


def get_hash(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_meta(path):
    with open(path, 'rb') as zip_file:
        content = zipfile.ZipFile(zip_file)
        zipball_hash = get_hash(path)
        info_file = content.open('{0}/info.json'.format(zipball_hash), 'r')
        raw_info = info_file.read()
        info_file.close()

    return json.loads(str(raw_info.decode('utf8')))


def get_broadcast_date(path):
    meta = get_meta(path)
    broadcast = meta.get('broadcast')
    if not broadcast:
        broadcast = meta.get('timestamp')

    return dateutil.parser.parse(broadcast).date()


def up(db, conf):
    db.executescript(SQL)

    contentd = conf['library.contentdir']
    zip_paths = [os.path.join(contentd, p) for p in os.listdir(contentd)
                 if p.endswith('.zip')]
    for path in zip_paths:
        try:
            zipball_hash = get_hash(path)
            broadcast_date = get_broadcast_date(path)
        except Exception:
            continue
        else:
            db.execute(DATA_SQL, (broadcast_date, zipball_hash))
