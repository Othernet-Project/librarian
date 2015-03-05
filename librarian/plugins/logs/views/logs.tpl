% rebase('_dashboard_section')

%# Translators, used as note in Application logs section
<p>{{ _('Logs are shown in reverse chronological order') }}</p>
<textarea>{{ logs }}</textarea>
<p><a class="button" href="{{ url('sys:logs') }}">{{ _('Download application log') }}</a></p>
