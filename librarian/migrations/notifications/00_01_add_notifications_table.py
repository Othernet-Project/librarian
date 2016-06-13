SQL = """
create table notifications
(
    notification_id varchar primary key,                   -- notification id
    message varchar,                                       -- notification message
    category varchar,                                      -- notification category
    icon varchar,                                          -- css class that provides icon
    priority integer not null default 0,                   -- urgency level
    created_at timestamptz not null,                       -- timestamp when notification was created
    read_at timestamptz,                                   -- timestamp when notification was read
    expires_at timestamptz,                                -- timestamp when notification expires
    dismissable boolean not null default false,            -- indicates whether notification can be marked as read
    groupable boolean not null default true,               -- indicates whether notification can be gathered into groups
    username varchar                                       -- username of recipient
);
"""


def up(db, conf):
    db.executescript(SQL)
