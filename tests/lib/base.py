import mock
import shutil
import tempfile

from librarian.app import in_pkg
from librarian.lib import squery
from librarian.utils import migrations


def transaction_test(bottle_request_paths):
    def _transaction_test(func):
        def __transaction_test(*args, **kwargs):
            paths = bottle_request_paths
            if isinstance(paths, str):
                paths = [paths]

            conn = squery.Connection()
            db = squery.Database(conn)
            config = {'content.contentdir': tempfile.mkdtemp()}
            migrations.migrate(db,
                               in_pkg('migrations'),
                               'librarian.migrations',
                               config)

            patchers = []
            for brp in paths:
                patcher = mock.patch(brp)
                bottle_request = patcher.start()
                bottle_request.db = db
                patchers.append(patcher)

            result = func(*args, **kwargs)

            [p.stop() for p in patchers]

            shutil.rmtree(config['content.contentdir'])
            return result

        return __transaction_test
    return _transaction_test
