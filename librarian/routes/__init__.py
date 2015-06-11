# -*- coding: utf-8 -*-

"""
Retrieve routing configuration

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import apps
import auth
import content
import dashboard
import downloads
import notifications
import setup
import system
import tags


def install_routes(app):
    # Routing table
    #
    # Each route is in following format::
    #
    #     (name, callback,
    #      method, path, route_config_dict),
    #
    skip_plugins = app.config['librarian.skip_plugins']
    routes = (

        # Authentication

        ('auth:login_form', auth.show_login_form,
         'GET', '/login/', {}),
        ('auth:login', auth.login,
         'POST', '/login/', {}),
        ('auth:logout', auth.logout,
         'GET', '/logout/', {}),

        # Content

        ('content:list', content.content_list,
         'GET', '/', {}),
        ('content:sites_list', content.content_sites_list,
         'GET', '/sites/', {}),
        ('content:zipball', content.content_zipball,
         'GET', '/pages/<content_id>.zip',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('content:reader', content.content_reader,
         'GET', '/pages/<content_id>', {}),
        ('content:delete', content.remove_content,
         'POST', '/delete/<content_id>', {}),
        # This is a static file route and is shadowed by the static file server
        ('content:file', content.content_file,
         'GET', '/content/<content_path:re:[0-9a-f]{3}(/[0-9a-f]{3}){9}/[0-9a-f]{2}>/<filename:path>',  # NOQA
         dict(no_i18n=True, skip=skip_plugins)),

        # Files

        ('files:list', content.show_file_list,
         'GET', '/files/', dict(unlocked=True)),
        ('files:path', content.show_file_list,
         'GET', '/files/<path:path>', dict(unlocked=True)),
        ('files:action', content.handle_file_action,
         'POST', '/files/<path:path>', dict(unlocked=True)),

        # Tags

        ('tags:list', tags.tag_cloud,
         'GET', '/tags/', {}),
        ('tags:edit', tags.edit_tags,
         'POST', '/tags/<content_id>', {}),

        # Downloads (Updates)

        ('downloads:list', downloads.list_downloads,
         'GET', '/downloads/', {}),
        ('downloads:action', downloads.manage_downloads,
         'POST', '/downloads/', {}),

        # Dashboard

        ('dashboard:main', dashboard.dashboard,
         'GET', '/dashboard/', {}),

        # Setup wizard

        ('setup:main', setup.setup_wizard,
         ['GET', 'POST'], '/setup/', {}),

        # Apps

        ('apps:list', apps.show_apps,
         'GET', '/apps/', dict(unlocked=True)),
        ('apps:app', apps.send_app_file,
         'GET', '/apps/<appid>/', dict(unlocked=True)),
        ('apps:asset', apps.send_app_file,
         'GET', '/apps/<appid>/<path:path>', dict(unlocked=True)),

        # Notifications

        ('notifications:list', notifications.notification_list,
         'GET', '/notifications/', {}),
        ('notifications:read', notifications.notifications_read,
         'POST', '/notifications/', {}),

        # System

        ('sys:static', system.send_static,
         'GET', '/static/<path:path>',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:favicon', system.send_favicon,
         'GET', '/favicon.ico',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:librarian_log', system.send_librarian_log,
         'GET', '/librarian.log',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:syslog', system.send_syslog,
         'GET', '/syslog',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),

        # This route handler is added because unhandled missing pages cause
        # bottle to _not_ install any plugins, and some are essential to
        # rendering of the 404 page (e.g., i18n, sessions, auth).
        ('sys:all404', system.all_404,
         ['GET', 'POST'], '/<path:path>', dict()),
    )

    for route in routes:
        name, cb, method, path, kw = route
        (family, member) = name.split(':')
        if family in app.config['librarian.routes']:
            app.route(path, method, cb, name=name, **kw)

    app.error(403)(system.show_access_denied_page)
    app.error(404)(system.show_page_missing)
    app.error(500)(system.show_error_page)
    app.error(503)(system.show_maint_page)
