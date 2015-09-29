import collections
import logging
import uuid

import gevent


class TaskScheduler(object):
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    NOT_FOUND = 'NOT_FOUND'

    def __init__(self, consume_tasks_delay=1):
        self._queue = collections.OrderedDict()
        self.current_task = None
        self._consume_tasks_delay = consume_tasks_delay
        self._async(self._consume_tasks_delay, self._consume)

    def _generate_task_id(self):
        return uuid.uuid4()

    def get_status(self, task_id):
        if task_id in self._queue:
            return self.QUEUED
        if task_id == self.current_task:
            return self.PROCESSING
        return self.NOT_FOUND

    def _async(self, delay, fn, *args, **kwargs):
        return gevent.spawn_later(delay, fn, *args, **kwargs)

    def _execute(self, task_id, fn, args, kwargs):
        self.current_task = task_id
        try:
            fn(*args, **kwargs)
        except Exception:
            logging.exception("Task execution failed.")
        finally:
            self.current_task = None

    def _periodic(self, task_id, fn, args, kwargs, delay):
        self._execute(task_id, fn, args, kwargs)
        self._async(delay, self._periodic, task_id, fn, args, kwargs, delay)

    def _consume(self):
        try:
            (task_id, task) = self._queue.popitem(last=False)
        except KeyError:
            pass  # no task in the queue
        else:
            self._execute(task_id, *task)
        finally:
            self._async(self._consume_tasks_delay, self._consume)

    def schedule(self, fn, args=None, kwargs=None, delay=None, periodic=False):
        """Schedules a task for execution.

        If `delay` is not specified, the task will be put into a queue and
        honor the existing order of scheduled tasks, being executed only after
        the tasks scheduled prior to it are completed.

        If `delay` is specified, the task will be scheduled to run NOT BEFORE
        the specified amount of seconds, not following any particular order,
        but there is no guarantee that it will run in exactly that time.

        The `periodic` flag has effect only on tasks that specified a `delay`,
        and those tasks will be rescheduled automatically for the same `delay`
        every time after they are executed.

        :param fn:        Function to execute
        :param args:      Tuple containing positional arguments for `fn`
        :param kwargs:    Dict containing keyword arguments for `fn`
        :param delay:     Int - execute `fn` in `delay` seconds
        :param periodic:  Boolean flag indicating if `fn` is a repeating task
        """
        args = args or tuple()
        kwargs = kwargs or dict()
        task_id = self._generate_task_id()
        if delay is None:
            self._queue[task_id] = (fn, args, kwargs)
        else:
            # async task, order does not matter
            if periodic:
                self._async(delay,
                            self._periodic,
                            task_id,
                            fn,
                            args,
                            kwargs,
                            delay)
            else:
                self._async(delay, self._execute, task_id, fn, args, kwargs)


def scheduler_plugin(app):
    delay = app.config['scheduler.delay']
    app.exts.tasks = TaskScheduler(consume_tasks_delay=delay)
