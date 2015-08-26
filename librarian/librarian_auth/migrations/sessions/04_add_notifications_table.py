SQL = """
create table notifications
(
    notification_id varchar primary_key unique not null,   -- notification id
    message varchar,                                       -- notification message
    category varchar,                                      -- notification category
    icon varchar,                                          -- css class that provides icon
    priority integer not null default 0,                   -- urgency level
    created_at timestamp not null,                         -- timestamp when notification was created
    read_at timestamp,                                     -- timestamp when notification was read
    expires_at timestamp,                                  -- timestamp when notification expires
    dismissable boolean not null default 0,                -- indicates whether notification can be marked as read
    user varchar                                           -- username of recipient
);
"""


def up(db, conf):
    db.executescript(SQL)
