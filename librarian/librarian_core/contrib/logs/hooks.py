import logging.config


def initialize(supervisor):
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
                'filename': supervisor.config['logging.output'],
                'maxBytes': supervisor.config['logging.size'],
                'backupCount': supervisor.config['logging.backups'],
            },
        },
        'formatters': {
            'default': {
                'format': supervisor.config['logging.format'],
                'datefmt': supervisor.config['logging.date_format'],
            },
        },
    })
