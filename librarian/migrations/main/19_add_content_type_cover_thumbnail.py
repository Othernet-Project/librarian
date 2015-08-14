SQL = """
alter table zipballs add column content_type int not null default 2;
alter table zipballs add column cover varchar not null default "cover.jpg";
alter table zipballs add column thumbnail varchar not null default "thumbnail.png";
"""


def up(db, conf):
    db.executescript(SQL)
