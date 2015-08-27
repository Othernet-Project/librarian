from .routes import (show_access_denied_page,
                     show_page_missing,
                     show_error_page,
                     show_main_page)


def init_begin(supervisor):
    supervisor.app.error(403)(show_access_denied_page)
    supervisor.app.error(404)(show_page_missing)
    supervisor.app.error(500)(show_error_page)
    supervisor.app.error(503)(show_main_page)
