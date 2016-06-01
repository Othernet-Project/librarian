

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

    def run(self, arg, supervisor):
        supervisor.events.subscribe(supervisor.POST_START, self.repl_start)
        supervisor.events.subscribe(supervisor.SHUTDOWN, self.repl_shutdown)
