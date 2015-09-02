<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title for page that shows result of running a script
${_('Script output')}
</%block>

<div class="h-bar">
    ## Translators, used as page header for page that shows result of running a script
    <h2>${_('Script output')}</h2>
</div>

<div class="full-page-form">
    ## Translators, return (result) code of the script executed via file browser
    <h2>${_('Return code:')}</h2>
    % if ret == 0:
    ## Translators, shown when result code is good (0).
    <span>0 ${_('OK')}</span>
    % else:
    ## Translators, shown when result code is not good (non-zero).
    <span>${ret} ${_('error')}</span>
    % endif

    ## Translators, refers to standard output of script run from file browser (STDOUT)
    <h2>${_('Output:')}</h2>
    % if out:
    <pre>${out}</pre>
    % else:
    ## Translators, shown if script returned no output
    <pre>${_('no output')}</pre>
    % endif

    % if err:
    ## Translators, refers to standard errors of script run from file browser (STDERR)
    <h2>${_('Errors')}</h2>
    <pre>${err}</pre>
    % endif
</div>
