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
    ${h.form('POST', action=i18n_url('setup:main'))}
        ${h.vinput('step', {'step': step_index}, _type='hidden')}
        <%block name="step"/>
        <button type="submit" name="action" value="next">${_('Next')}</button>
    </form>
</div>
</%block>
