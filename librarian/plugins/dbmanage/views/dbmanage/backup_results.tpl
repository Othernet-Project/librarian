<%inherit file="base">

<%block name="title">
## Translators, used as page title
${_('Database backup')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Database backup')}
</%block>

% if path:
    <p>${_('Database backup has been completed successfully. You will be taken to the backup folder in 10 seconds.')}</p>
    % if time:
        <p>${ngettext('The operation took %s second', 'The operation took %s seconds', time) % round(time, 2)}</p>
    % endif
% elif error:
    <p>${_('Database backup could not be completed. The following error occurred:')}</p>
    <p>${error}</p>
% endif


