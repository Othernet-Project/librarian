import os


SQL = """
create table folders
(
    id serial primary key,
    path varchar unique not null,
    facet_types smallint default 1, -- generic
    main varchar  -- e.g. html index
);
alter table facets rename to tmp;
create table facets
(
    path varchar unique not null,
    folder integer references folders (id),
    facet_types smallint default 1, -- generic
    author varchar default '',
    description varchar default '',
    title varchar default '',
    genre varchar default '',
    album varchar default '',
    width int default 0,
    height int default 0,
    duration int default 0,
    keywords varchar,
    copyright varchar,
    language varchar,
    outernet_formatting boolean
);
create unique index on facets (path);
create index on facets (path, facet_types);
"""
DROP_TMP_SQL = 'drop table tmp;'


def up(db, conf):
    db.executescript(SQL)
    folders = dict()
    for row in db.fetchiter(db.Select(sets='tmp')):
        row = dict(row)
        path = row['path']
        if path not in folders:
            # create folder entry
            q = db.Insert('folders', cols=['path', 'facet_types'])
            db.execute(q, dict(path=path, facet_types=row['facet_types']))
            q = db.Select(sets='folders', where='path = %s')
            folder = db.fetchone(q, (path,))
            folders[path] = dict((k, folder[k]) for k in folder.keys())
        else:
            # update bitmask on existing folder data
            folders[path]['facet_types'] |= row['facet_types']
        # copy facet item into new table, with additional folder id and
        # concatenated `path` and `file` columns
        row.update(path=os.path.normpath(os.path.join(path, row.pop('file'))),
                   folder=folders[path]['id'])
        q = db.Insert('facets', cols=row.keys())
        db.execute(q, row)
    # update folder entries with collected bitmasks of all it's children
    q = db.Update('folders',
                  facet_types='%(facet_types)s',
                  where='id = %(id)s')
    db.executemany(q, folders.values())
    db.executescript(DROP_TMP_SQL)
