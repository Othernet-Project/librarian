%# Translators, used as page title for page that shows result of running a script
% rebase('base.tpl', title=_('Script output'))
<h1>
%# Translators, used as page header for page that shows result of running a script
{{ _('Script output') }}
</h1>

<div class="inner">
    <p>
    %# Translators, return (result) code of the script executed via file browser
    <strong>{{ _('return code:') }}</strong>
    % if ret == 0:
    %# Translators, shown when result code is good (0).
    0 {{ _('OK') }}
    % else:
    %# Translators, shown when result code is not good (non-zero).
    {{ ret }} {{ _('error') }}
    % end
    </p>

    %# Translators, refers to standard output of script run from file browser (STDOUT)
    <h2>{{ _('Output') }}</h2>
    % if out:
    <pre>{{ out }}</pre>
    % else:
    %# Translators, shown if script returned no output
    <pre>{{ _('no output') }}</pre>
    % end

    % if err:
    %# Translators, refers to standard errors of script run from file browser (STDERR)
    <h2>{{ _('Errors') }}</h2>
    <pre>{{ err }}</pre>
    % end
</div>
