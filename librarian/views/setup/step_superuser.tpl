<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please enter the desired credentials for the superuser account.')}</h3>
<div class="step-superuser-form">
    <p>
        ${form.username.label}
        ${form.username}
        % if form.username.error:
        ${form.username.error}
        % endif
    </p>
    <p>
        ${form.password1.label}
        ${form.password1}
        % if form.password1.error:
        ${form.password1.error}
        % endif
    </p>
    <p>
        ${form.password2.label}
        ${form.password2}
        % if form.password2.error:
        ${form.password2.error}
        % endif
    </p>
    % if form.error:
    ${form.error}
    % endif
</div>
</%block>
