% rebase('base', redirect=path)
<h1>
%# Translators, used as page heading
{{ _('Database backup') }}
</h1>

<div class="inner">
% if path:
    <p>{{ _('Database backup has been completed successfully. You will be taken to the backup folder in 10 seconds.') }}</p>
    % if time:
        <p>{{ u(ngettext('The operation took %s second', 'The operation took %s seconds', time)) % round(time, 2) }}</p>
    % end
% elif error:
    <p>{{ _('Database backup could not be completed. The following error occurred:') }}</p>
    <p>{{ error }}</p>
% end
</div>


