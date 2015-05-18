"""
repl.py: Python shell for librarian

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import code
import sys
import threading

from gevent import fileobject


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


_green_stdin = fileobject.FileObject(sys.stdin)
_green_stdout = fileobject.FileObject(sys.stdout)


def _green_raw_input(prompt):
    _green_stdout.write(prompt)
    _green_stdout.flush()
    return _green_stdin.readline()[:-1]


def repl_factory(local, exit_message):
    def repl_starter():
        code.interact(BANNER, _green_raw_input, local=local)
        print(exit_message)
    return repl_starter


def start_repl(local={}, exit_message='Exiting'):
    """ Start Librarian REPL interface in a separate thread

    :param local:   dictionary representing local context for the REPL
    :returns:       ``threading.Thread`` object
    """
    thread = threading.Thread(target=repl_factory(local, exit_message))
    thread.start()
    return thread
