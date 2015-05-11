<%inherit file='/base.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Setup Wizard')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Setup Wizard: Step %s of %s') % (step_index, step_count)}
</%block>

<%block name="header"></%block>

<%block name="inner">
<div class="setup-wizard">
    ${h.form('POST', action=i18n_url('setup:main') + h.set_qparam(**{step_param: step_index}).to_qs())}
        <%block name="step"/>
        % if step_index - 1 >= start_index:
        <a class="button" href="${i18n_url('setup:main') + h.set_qparam(**{step_param: step_index - 1}).to_qs()}">${_('Back')}</a>
        % endif
        <button type="submit" name="action" value="next">${_('Next')}</button>
    </form>
</div>
</%block>
