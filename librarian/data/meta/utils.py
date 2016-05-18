import datetime
import functools
import logging
import subprocess

import gevent


def run_command(command, timeout, debug=False):
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    if debug:
        logging.debug('Command (%s) started at pid %s',
                      ' '.join(command),
                      process.pid)
    while process.poll() is None:
        gevent.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            if debug:
                logging.debug('Command (%s) timed out(>%s secs). Terminating.',
                              ' '.join(command),
                              timeout)
            process.kill()
            return (None, None)
    if debug:
        logging.debug('Command with pid %s ended normally with return code %s',
                      process.pid,
                      process.returncode)
    return (process.returncode, process.stdout.read())


def runnable(timeout=5, debug=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd = func(*args, **kwargs)
            return run_command(cmd, timeout=timeout, debug=debug)
        return wrapper
    return decorator
