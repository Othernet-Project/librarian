from greentasks.scheduler import TaskScheduler

from ...exports import hook


@hook('initialize')
def initialize(supervisor):
    delay = supervisor.config['app.consume_tasks_delay']
    supervisor.exts.tasks = TaskScheduler(consume_tasks_delay=delay)
