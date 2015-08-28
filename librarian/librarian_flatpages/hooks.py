from .flat import FlatPageRegistry


def initialize(supervisor):
    flat_root = supervisor.config['flat.root']
    supervisor.exts.flat_pages = FlatPageRegistry(flat_root)
