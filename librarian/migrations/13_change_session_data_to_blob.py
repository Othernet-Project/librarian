import json, cPickle as pickle, sqlite3
from cStringIO import StringIO

SQL = """
alter table sessions rename to tmp;
create table sessions
(
    session_id varchar primary_key unique not null,   -- session id
    data blob,                                        -- pickled session data
    expires timestamp not null                        -- timestamp when session expires
);
"""


def _to_pickle(data):
    data = json.loads(data)
    f = StringIO()
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    f.seek(0)
    return sqlite3.Binary(f.read())


def up(db, conf):
    db.executescript(SQL)
    db.query(db.Select(['session_id', 'data', 'expires'], sets='tmp'))
    new_data = []
    for r in db.cursor:
        new_data.append((r.session_id, _to_pickle(r.data), r.expires))
    db.executemany(
        db.Insert('sessions',
                  cols=['session_id', 'data', 'expires'],
                  vals=', '.join('?' * 3)),
        new_data)
    db.execute('DROP TABLE tmp;')

