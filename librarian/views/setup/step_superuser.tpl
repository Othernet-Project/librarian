<%inherit file='/setup/setup_base.tpl'/>

<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="note" file="/auth/_reset_token.tpl"/>

<%block name="step_title">
    <span class="icon icon-user-up"></span>
    ${_('Superuser account')}
</%block>

<%block name="step_desc">
    <p>
        ${_('The superuser account is used to maintain the library and configure the receiver.')}
    </p>
</%block>

<%block name="step">
<div class="step-superuser-form">
    % if form.error:
    ${form.error}
    % endif
    ${forms.field(form.username)}
    ${forms.field(form.password1)}
    ${forms.field(form.password2)}
    ${note.token_note(reset_token)}
</div>
</%block>
