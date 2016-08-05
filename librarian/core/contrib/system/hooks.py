import tempfile

from ...exports import hook
from ...exts import ext_container as exts


@hook('initialize')
def initialize(supervisor):
    tempfile.tempdir = exts.config['tempfile.tempdir']
