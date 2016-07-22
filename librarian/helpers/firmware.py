import logging
import os
import stat
import subprocess

from ..core.exts import ext_container as exts


FIRMWARE_UPDATE_KEY = 'firmware_update_status'


def save_firmware(firmware, save_path):
    if os.path.exists(save_path):
        logging.debug('Replacing firmware update file')
        os.remove(save_path)
    logging.debug('Saving firmware at %s', save_path)
    firmware.save(save_path)
    # make firmware executable
    mode = (stat.S_IRWXU |
            stat.S_IRGRP |
            stat.S_IXGRP |
            stat.S_IROTH |
            stat.S_IXOTH)
    os.chmod(save_path, mode)


def update_firmware(firmware, save_path):
    try:
        save_firmware(firmware, save_path)
    except Exception:
        logging.exception('Failed to save firmware update.')
        exts.cache.set(FIRMWARE_UPDATE_KEY, 'failed')
    else:
        try:
            subprocess.check_call(save_path, shell=True)
        except subprocess.CalledProcessError:
            logging.exception('Failed to execute firmware update.')
            exts.cache.set(FIRMWARE_UPDATE_KEY, 'failed')
