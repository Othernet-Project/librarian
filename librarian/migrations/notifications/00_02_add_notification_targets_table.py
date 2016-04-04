SQL = """
create table notification_targets
(
    target_id varchar PRIMARY KEY UNIQUE,               -- id of target rule
    notification_id varchar REFERENCES notifications (notification_id),     -- notification id
    target_type varchar,                                -- type of target to use
    target varchar                                      -- identifying charactaristic of recipient
);
"""


def up(db, conf):
    db.executescript(SQL)
