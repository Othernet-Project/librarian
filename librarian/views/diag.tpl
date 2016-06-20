<%inherit file='narrow_base.tpl'/>

<%block name="title">
${_("Diagnostics")}
</%block>

<div class="h-bar">
    ## Translators, used as page title
    <h2>${_('Diagnostics')}</h2>
</div>

<%block name="narrow_main">
<div class="diag">
    <table>
        <tr>
            <td>${_("Version")}</td>
            <td>${th.app_version()}</td>
        </tr>
        <tr>
            <td>${_("Has tuner?")}</td>
            <td>${h.yesno(has_tuner, h.SPAN(_('Yes'), _class='has-tuner'), h.SPAN(_('No'), _class='no-tuner'))}</td>
        </tr>
    </table>
    <textarea>${''.join(logs)}</textarea>
</div>
</%block>
