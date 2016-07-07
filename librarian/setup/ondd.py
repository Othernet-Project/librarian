import logging

from bottle import request
from bottle_utils.i18n import lazy_gettext as _

from ..forms import ondd as ondd_forms
from ..helpers import ondd as ondd_helpers


def get_form():
    """
    Return appropriate form class for configured frequency band
    """
    return ondd_forms.FORMS[ondd_helpers.get_band()]


class ONDDStep:
    name = 'ondd'
    index = 30
    template = 'setup/step_ondd.tpl'

    @staticmethod
    def test():
        ondd_client = request.app.supervisor.exts.ondd
        ondd_alive = ondd_client.ping()
        if not ondd_alive:
            # If ondd is not running, skip the step
            return False
        settings = ondd_helpers.read_ondd_setup()
        if settings is None:
            # Settings is None if ONDD configuration has never been performed
            return True
        if settings == {}:
            # Settings is a dict if settings has been performed by no preset
            # is present. This is allowed, as user is allowed to skip through
            # the setup step without setting the tuner settings.
            return False
        ONDDForm = get_form()
        form = ONDDForm(ondd_helpers.read_ondd_setup())
        return not form.is_valid()

    @staticmethod
    def get():
        ondd_client = request.app.supervisor.exts.ondd
        snr_min = request.app.config.get('ondd.snr_min', 0.2)
        snr_max = request.app.config.get('ondd.snr_max', 0.9)
        return dict(status=ondd_client.get_status(), form=ONDDForm(),
                    SNR_MIN=snr_min, SNR_MAX=snr_max)

    @staticmethod
    def post():
        ondd_client = request.app.supervisor.exts.ondd
        is_test_mode = request.forms.get('mode', 'submit') == 'test'
        ONDDForm = get_form()
        form = ONDDForm(request.forms)
        form_valid = form.is_valid()
        snr_min = request.app.config.get('ondd.snr_min', 0.2)
        snr_max = request.app.config.get('ondd.snr_max', 0.9)

        if form_valid:
            # Store full settings
            logging.info('ONDD: tuner settings updated')
            data = {'ondd': form.processed_data}
            request.app.supervisor.exts.setup.append(data)

            if is_test_mode:
                return dict(successful=False, form=form,
                            status=ondd_client.get_status(),
                            # Translators, shown when tuner settings are
                            # updated during setup wizard step.
                            message=_('Tuner settings have been updated'),
                            SNR_MIN=snr_min, SNR_MAX=snr_max)
            return dict(successful=True)

        # Form is not valid
        if is_test_mode:
            # We only do something about this in test mode
            return dict(successful=False, form=form,
                        status=ondd_client.get_status(),
                        SNR_MIN=snr_min, SNR_MAX=snr_max)

        request.app.supervisor.exts.setup.append({'ondd': {}})
        return dict(successful=True)
