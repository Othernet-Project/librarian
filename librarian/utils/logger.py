"""
logger.py: Configure logger

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging.config
import os

from .system import ensure_dir


def configure_logger(app):
    logfile = app.args.log or app.config['logging.output']
    ensure_dir(os.path.dirname(logfile))
    logging.config.dictConfig({
        'version': 1,
        'root': {
            'handlers': ['file'],
            'level': logging.DEBUG,
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': logfile,
                'maxBytes': app.config['logging.size'],
                'backupCount': app.config['logging.backups'],
            },
        },
        'formatters': {
            'default': {
                'format': app.config['logging.format'],
                'datefmt': app.config['logging.date_format'],
            },
        },
    })
