from .. import __version__ as _version, __author__ as _author

__version__ = _version
__author__ = _author
__all__ = ('dashboard_app', 'content_app', 'downloads_app', 'favorites_app',)

from .dashboard import app as dashboard_app
from .content import app as content_app
from .downloads import app as downloads_app
from .favorites import app as favorites_app
