import os


SQL = """
create table fs
(
    id serial primary key,
    parent_id integer not null default 0,
    path varchar unique not null,
    type smallint not null,
    content_types smallint not null default 1 -- generic
);
create unique index on fs (path);
create index on fs (path, content_types);
create table meta
(
    id serial primary key,
    fs_id integer references fs (id),
    language varchar,
    key varchar,
    value varchar,
    unique (fs_id, language, key)
);
"""
DROP_OLD_TABLE_SQL = 'drop table facets;'


def add_fs(db, path, parent_id=0, content_types=1):
    q = db.Replace('fs',
                   constraints=['path'],
                   cols=['path', 'parent_id', 'content_types'])
    params = dict(path=path, parent_id=parent_id, content_types=content_types)
    db.execute(q, params)
    q = db.Select(sets='fs', where='path = %s')
    return dict(db.fetchone(q, (path,)))


def ancestors(path):
    normalized = os.path.normpath(path)
    if normalized == os.path.sep:
        yield normalized
    elif normalized == '.':
        yield ''
    else:
        parts = normalized.split(os.path.sep)
        if parts[0]:
            yield ''
        for i in range(len(parts)):
            yield os.path.sep.join(parts[0:i + 1]) or os.path.sep


def up(db, conf):
    db.executescript(SQL)
    folders = dict()
    for row in db.fetchiter(db.Select(sets='facets')):
        row = dict(row)
        facet_types = row.pop('facet_types')
        # filenames and paths are separated in old table, so parent is ``path``
        parent_path = os.path.normpath(row.pop('path'))
        try:
            parent = folders[parent_path]
        except KeyError:
            # make sure all ancestors up to root are created
            parent_id = 0
            for path in ancestors(parent_path):
                if path not in folders:
                    # create folder entry
                    parent = add_fs(db, path, parent_id=parent_id)
                    folders[path] = parent
                else:
                    parent = folders[path]
                parent_id = parent['id']
        # update bitmask on existing folder data
        parent['content_types'] |= facet_types
        # copy facet item into new table, with additional folder id and
        # concatenated `path` and `file` columns
        filepath = os.path.normpath(os.path.join(parent_path, row.pop('file')))
        if filepath not in folders:
            # files and folders are mixed up in old table
            file_fs = add_fs(db,
                             filepath,
                             parent_id=parent['id'],
                             content_types=facet_types)
        # add remaining data se meta entries
        for (key, value) in row.items():
            # skip unset data
            if value:
                q = db.Insert('meta', cols=['fs_id', 'key', 'value'])
                db.execute(q, dict(fs_id=file_fs['id'], key=key, value=value))
    # update folder entries with collected bitmasks of all it's children
    q = db.Update('fs', content_types='%(content_types)s', where='id = %(id)s')
    db.executemany(q, folders.values())
    db.executescript(DROP_OLD_TABLE_SQL)
