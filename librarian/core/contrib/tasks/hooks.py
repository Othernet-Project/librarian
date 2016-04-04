from greentasks.scheduler import TaskScheduler


def initialize(supervisor):
    delay = supervisor.config['app.consume_tasks_delay']
    supervisor.exts.tasks = TaskScheduler(consume_tasks_delay=delay)
