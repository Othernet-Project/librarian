SQL = """
create index on facets (path);
create index on facets (path, facet_types);
"""


def up(db, conf):
    db.executescript(SQL)
