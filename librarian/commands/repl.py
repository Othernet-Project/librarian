from ..core.exts import ext_container as exts


class ReplCommand(object):
    name = 'repl'
    flags = '--repl'
    kwargs = {
        'action': 'store_true',
        'help': "Start interactive shell after servers start"
    }

    def repl_start(self, supervisor):
        from ..utils.repl import start_repl
        namespace = dict(supervisor=supervisor)
        message = 'Press Ctrl-C to shut down Librarian.'
        self.repl_thread = start_repl(namespace, message)

    def repl_shutdown(self, supervisor):
        self.repl_thread.join()

    def run(self, args):
        if not args.repl:
            return

        exts.events.subscribe('post_start', self.repl_start)
        exts.events.subscribe('shutdown', self.repl_shutdown)
