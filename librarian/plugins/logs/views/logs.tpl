% rebase('_dashboard_section')

%# Translators, used as note in Application logs section
<p>{{ _('Logs are shown in reverse chronological order') }}</p>
<textarea>\\
% for line in logs:
{{ line }}\\
% end
</textarea>
<p><a class="button" href="{{ url('sys:logs') }}">{{ _('Download application log') }}</a></p>
