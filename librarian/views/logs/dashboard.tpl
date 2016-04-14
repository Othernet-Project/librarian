## Translators, used as note in Application logs section
<p>${_('Logs are shown in reverse chronological order')}</p>
<textarea>${u''.join([h.to_unicode(line) for line in logs])}</textarea>
<p>
    ## Translators, used as label for a button that allows download of system logs
    <a class="button" href="${url('logs:send_diag')}">${_('Download system logs')}</a>
</p>
