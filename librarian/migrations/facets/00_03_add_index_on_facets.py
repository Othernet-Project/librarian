SQL = """
create unique index on facets (path, file)
"""


def up(db, conf):
    db.executescript(SQL)
