"""
favorites.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request

__all__ = ('favorite_content', 'mark_favorite',)

FAVS_QUERY = """
SELECT * FROM zipballs
WHERE favorite = 1
ORDER BY views DESC, updated DESC;
"""
MARK_FAV_QUERY = """
UPDATE zipballs
SET favorite = :fav
WHERE md5 = :md5;
"""


def favorite_content(limit=None):
    """ Query database for favorited content

    :param limit:   optional limit on number of items to fetch
    :returns:       iterable of dbdict objects
    """
    # TODO: Unit tests
    db = request.db
    if limit:
        db.query(FAVS_QUERY.strip(';\n ') + ' LIMIT ?;', limit)
    else:
        db.query(FAVS_QUERY)
    return db.cursor.fetchall()


def mark_favorite(md5, val=1):
    """ Mark archive record with MD5 key as favorite

    :param md5:     primary key of the record
    :param val:     favorite value, set it to 1 for favorite, 0 for unfavorite
    :returns:       ``True`` if update was successful, ``False`` otherwise
    """
    # TODO: Unit tests
    db = request.db
    db.query(MARK_FAV_QUERY, fav=val, md5=md5)
    db.commit()
    return db.cursor.rowcount == 1

