<%inherit file="/narrow_base.tpl"/>

<%block name="title">
    ${_('Setup wizard')}
</%block>

<%block name="extra_head">
    <link rel="stylesheet" href="${assets['css/wizard']}">
</%block>

<%block name="header">
    <div class="wizard-steps">
    % for i in range(1, step_count + 1):
        % if i < step_index:
            <span class="step">
                <span class="icon icon-circle-ok"></span>
        % elif i == step_index:
            <span class="step">
                <span class="icon icon-circle-dot"></span>
        % else:
            <span class="step">
                <span class="icon icon-circle"></span>
        % endif
        </span>
    % endfor
    </div>
</%block>

<%block name="narrow_main">
    <div class="section body">
        <h2 class="step-logo step-${step_name}">
            <%block name="step_title"/>
        </h2>
        <%block name="step_desc"/>
        <div class="setup-wizard full-page-form">
            ${h.form('POST', action=i18n_url('setup:main') + h.set_qparam(**{step_param: step_index}).to_qs())}
                <%block name="step"/>
                <p class="buttons">
                    % if step_index - 1 >= start_index:
                        <a class="button" href="${i18n_url('setup:main', step_param=step_index - 1)}">${_('Back')}</a>
                    % endif
                    <button type="submit" name="action" value="next">${_('Finish') if step_index == step_count else _('Next')}</button>
                </p>
            </form>
        </div>
    </div>
</%block>

<%block name="footer">
</%block>

<%block name="script_templates"/>
<%block name="extra_scripts">
    <script type="text/javascript" src="${assets['js/wizard']}"></script>
</%block>
