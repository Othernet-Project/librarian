"""
hooks.py: Register app hooks

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


COMMANDS = 'commands'  # register command line arg handlers
PRE_START = 'pre_start'  # low-level initialization
START = 'start'  # higher-level initialization, just before starting the server
POST_START = 'post_start'
BACKGROUND = 'background'
SHUTDOWN = 'shutdown'
APP_HOOKS = (COMMANDS, PRE_START, START, POST_START, BACKGROUND, SHUTDOWN)


def register_hooks(app):
    for hook_name in APP_HOOKS:
        for hook_path in app.config.get('hooks.{0}'.format(hook_name), []):
            mod_path = hook_path.split('.')
            func_name = mod_path[-1]
            mod = __import__('.'.join(mod_path[:-1]), fromlist=[func_name])
            hook_func = getattr(mod, func_name)
            app.events.subscribe(hook_name, hook_func)
