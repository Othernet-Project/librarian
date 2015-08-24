import os


def check_integrity(config):
    return bool(os.listdir(config['recovery.dirtydir']))
