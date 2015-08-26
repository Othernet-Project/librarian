import os

SQL = 'update zipballs set size = ? where md5 = ?;'


def get_hash(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_size(path):
    return os.stat(path).st_size


def up(db, conf):
    contentd = conf['library.contentdir']
    paths = [os.path.join(contentd, p)
             for p in os.listdir(contentd)
             if p.endswith('.zip')]

    db.executemany(SQL, ((get_size(p), get_hash(p)) for p in paths))
