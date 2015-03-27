<%inherit file="../base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Database rebuild')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Database rebuild')}
</%block>

% if redirect:
    <p>${_('Content database has been rebuilt from scratch. A backup copy of the original database has been created. You will find it in the files section.')}</p>
    % if time:
        <p>${ngettext('The operation took %s second', 'The operation took %s seconds', time) % round(time, 2)}</p>
    % endif
% elif error:
    <p>${_('Database could not be rebuilt. The following error occurred:')}</p>
    <p>${error}</p>
% endif


