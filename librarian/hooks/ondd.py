from ondd_ipc.ipc import ONDDClient

from .dashboard_plugin import ONDDDashboardPlugin
from .setup import has_invalid_config, setup_ondd_form, setup_ondd
from .tasks import query_cache_storage_status


def initialize(supervisor):
    supervisor.exts.ondd = ONDDClient(supervisor.config['ondd.socket'])
    supervisor.exts.dashboard.register(ONDDDashboardPlugin)
    # register setup wizard step
    setup_wizard = supervisor.exts.setup_wizard
    setup_wizard.register('ondd',
                          setup_ondd_form,
                          template='setup/step_ondd.tpl',
                          method='GET',
                          test=has_invalid_config)
    setup_wizard.register('ondd',
                          setup_ondd,
                          template='setup/step_ondd.tpl',
                          method='POST',
                          test=has_invalid_config)

    refresh_rate = supervisor.config['ondd.cache_refresh_rate']
    supervisor.exts.tasks.schedule(query_cache_storage_status,
                                   args=(supervisor,),
                                   delay=refresh_rate,
                                   periodic=True)

