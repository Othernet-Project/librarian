"""
links.py: Module to maintain linked content files
"""

from sqlize_pg.builder import Replace, Delete, Select

from librarian_core.exts import ext_container as exts


TABLE_NAME = 'links'

REPLACE_QUERY = Replace(TABLE_NAME,
                        constraints=['source', 'target'],
                        cols=['source', 'target'])

DELETE_PARTIAL_QUERY = Delete(TABLE_NAME, where='source = %s and target = %s')

DELETE_ALL_QUERY = Delete(TABLE_NAME, where='source = %s')

SELECT_TARGET_QUERY = Select(sets=TABLE_NAME,
                             what='target',
                             where='source = %s')

SELECT_SOURCE_QUERY = Select(sets=TABLE_NAME,
                             what='source',
                             where='target = %s')


def _get_db():
    return exts.databases.facets


def add_links(source, targets):
    """
    Links ``source`` file with each relative path in ``targets`` parameter.
    """
    db = _get_db()
    db.executemany(REPLACE_QUERY,
                   (dict(source=source, target=target) for target in targets))


def remove_links(source, targets=None):
    """
    Remove links between ``source`` file and each relative path in ``targets``
    parameter. If ``target`` is None then it clears all files linked with
    ``source``.
    """
    db = _get_db()
    if targets is not None:
        for target in targets:
            db.execute(DELETE_PARTIAL_QUERY, (source, target))
    else:
        db.execute(DELETE_ALL_QUERY, (source,))


def get_links(source):
    """
    Returns list of paths linked with ``source`` file.
    """
    db = _get_db()
    return [row['target'] for row in db.fetchiter(
        SELECT_TARGET_QUERY, (source,))]


def get_sources(target):
    """
    Returns list of paths which are dependent on ``target`` file
    """
    db = _get_db()
    return [row['source'] for row in db.fetchiter(
        SELECT_SOURCE_QUERY, (target,))]


def update_links(source, targets=None, clear=True):
    """
    Updates list of paths linked with ``source`` file. If ``clear`` is True,
    all previous links are cleared.
    """
    if clear:
        remove_links(source)
    add_links(source, targets)
