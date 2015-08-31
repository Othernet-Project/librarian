

def repl_start(supervisor):
    from .repl import start_repl
    namespace = dict(supervisor=supervisor)
    message = 'Press Ctrl-C to shut down Librarian.'
    supervisor.repl_thread = start_repl(namespace, message)


def repl_shutdown(supervisor):
    supervisor.repl_thread.join()


def repl(arg, supervisor):
    supervisor.events.subscribe(supervisor.POST_START, repl_start)
    supervisor.events.subscribe(supervisor.SHUTDOWN, repl_shutdown)
