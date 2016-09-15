from greentasks import TaskScheduler

from ..exports import ObjectCollectorMixin, ListCollector
from ..exts import ext_container as exts


class Tasks(ObjectCollectorMixin, ListCollector):
    """
    Collects backgroung tasks of registered components.
    """
    export_key = 'tasks'

    def __init__(self, supervisor):
        super(Tasks, self).__init__(supervisor)
        delay = supervisor.config['tasks.consume_delay']
        multiprocessing = supervisor.config['tasks.multiprocessing']
        exts.tasks = TaskScheduler(consume_tasks_delay=delay,
                                   multiprocessing=multiprocessing)

    def install_member(self, task_cls):
        exts.tasks.schedule(task_cls)
