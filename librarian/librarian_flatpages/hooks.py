from .flat import FlatPageRegistry


def init_begin(supervisor):
    flat_root = supervisor.config['flat.root']
    supervisor.exts.flat_pages = FlatPageRegistry(flat_root)
