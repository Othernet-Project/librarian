<%inherit file='/base.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Setup Wizard')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Setup Wizard: Step %s of %s') % (step_index, step_count)}
</%block>

<div class="setup-wizard">
    ${h.form('POST', action=i18n_url('setup:main'))}
        ${step}
        <button type="submit" name="action" value="next">${_('Next')}</button>
    </form>
</div>
