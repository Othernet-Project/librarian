import pytz

from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from .lang import UI_LANGS, DEFAULT_LOCALE


class SetupLanguageForm(form.Form):
    # Translators, used as label for language
    language = form.SelectField(_('Language'),
                                value=DEFAULT_LOCALE,
                                validators=[form.Required()],
                                choices=UI_LANGS)


class SetupDateTimeForm(form.Form):
    TIMEZONES = [(tzname, tzname) for tzname in pytz.common_timezones]
    DEFAULT_TIMEZONE = pytz.common_timezones[0]
    # Translators, used as label for date and time setup
    timezone = form.SelectField(_("Timezone"),
                                value=DEFAULT_TIMEZONE,
                                validators=[form.Required()],
                                choices=TIMEZONES)
