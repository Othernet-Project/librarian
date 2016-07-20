import logging
import os
import stat


def update_firmware(firmware, save_path):
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
