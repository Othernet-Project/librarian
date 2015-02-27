% rebase('base', redirect=path)
<h1>
%# Translators, used as page heading
{{ _('Database rebuild') }}
</h1>

<div class="inner">
% if path:
    <p>{{ _('Content database has been rebuilt from scratch. A backup copy of the original database has been created. You will find it in the files section.') }}</p>
    % if time:
        <p>{{ u(ngettext('The operation took %s second', 'The operation took %s seconds', time)) % round(time, 2) }}</p>
    % end
% elif error:
    <p>{{ _('Database could not be rebuilt. The following error occurred:') }}</p>
    <p>{{ error }}</p>
% end
</div>


