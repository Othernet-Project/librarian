SQL = """
create table sessions
(
    session_id varchar primary key,       -- session id
    data varchar,                         -- arbitary session data
    expires timestamptz not null          -- timestamp when session expires
);
"""


def up(db, conf):
    db.executescript(SQL)
