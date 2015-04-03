"""
repl.py: Python shell for librarian

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import code
import threading


BANNER = """
===============================================================================
Librarian REPL
-------------------------------------------------------------------------------
You may use Librarian REPL to interact with RUNNING LIBRARIAN CODE. This is a
standard Python shell with access to objects that are present at runtime. A few
useful objects you can access are:

    `databases`: mapping of databases and respective Database objects
    `servers`: list of currently active gevent servers
    `config`: configuration dictionary

To exit the REPL, type exit() or Ctrl-D (Ctrl-Z followed by Enter on Windows).
===============================================================================
"""


def repl_factory(local):
    def repl_starter():
        code.interact(banner=BANNER, local=local)
    return repl_starter


def start_repl(local={}):
    """ Start Librarian REPL interface in a separate thread

    :param local:   dictionary representing local context for the REPL
    :returns:       ``threading.Thread`` object
    """
    thread = threading.Thread(target=repl_factory(local))
    thread.start()
    return thread
