SQL = """
create index target_index on links(target);
"""


def up(db, conf):
    db.executescript(SQL)
