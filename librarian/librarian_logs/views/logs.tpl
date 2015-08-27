<%inherit file="_dashboard_section.tpl"/>

## Translators, used as note in Application logs section
<p>${_('Logs are shown in reverse chronological order')}</p>
<textarea>${''.join(logs)}</textarea>
<p>
    <a class="button primary" href="${url('sys:librarian_log')}">${_('Download application log')}</a>
    <a class="button" href="${url('sys:syslog')}">${_('Download system log')}</a>
</p>
