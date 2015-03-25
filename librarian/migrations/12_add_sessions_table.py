SQL = """
create table sessions
(
    session_id varchar primary_key unique not null,   -- session id
    data varchar,                                     -- arbitary session data
    expires timestamp not null                        -- timestamp when session expires
);
"""


def up(db, conf):
    db.executescript(SQL)
