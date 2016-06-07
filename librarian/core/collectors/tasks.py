from ..exports import ObjectCollectorMixin, ListCollector


class Tasks(ObjectCollectorMixin, ListCollector):
    """
    Collects backgroung tasks of registered components.
    """
    export_key = 'tasks'

    def install_member(self, task_cls):
        # tasks need to be started only after server is running
        task_cls.install()
