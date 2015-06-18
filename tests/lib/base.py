import mock
import os
import shutil
import tempfile

import librarian

from librarian.lib import squery
from librarian.utils import migrations


def in_pkg(*paths):
    MODDIR = os.path.dirname(os.path.abspath(librarian.__file__))
    return os.path.normpath(os.path.join(MODDIR, *paths))


def transaction_test(bottle_request_paths):
    def _transaction_test(func):
        def __transaction_test(*args, **kwargs):
            paths = bottle_request_paths
            if isinstance(paths, str):
                paths = [paths]

            conn = squery.Connection()
            db = squery.Database(conn)
            config = {'content.contentdir': tempfile.mkdtemp()}
            migrations.migrate(db, 'librarian.migrations.sessions', config)
            patchers = []
            for brp in paths:
                patcher = mock.patch(brp)
                bottle_request = patcher.start()
                bottle_request.db.sessions = db
                patchers.append(patcher)

            bottle_request.app.config = {'session.lifetime': 1}
            result = func(*args, **kwargs)

            [p.stop() for p in patchers]

            shutil.rmtree(config['content.contentdir'])
            return result

        return __transaction_test
    return _transaction_test
