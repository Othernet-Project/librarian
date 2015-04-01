SQL = """
alter table zipballs add column keep_formatting boolean not null default 0;
alter table zipballs add column is_core boolean not null default 0;
alter table zipballs add column is_partner boolean not null default 0;
alter table zipballs add column is_sponsored boolean not null default 0;
alter table zipballs add column partner varchar;
alter table zipballs add column license varchar;
"""


def up(db, config):
    db.executescript(SQL)
