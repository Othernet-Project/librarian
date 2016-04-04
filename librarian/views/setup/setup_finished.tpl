<%inherit file="/narrow_base.tpl"/>

<%block name="extra_head">
    <link rel="stylesheet" href="${assets['css/setup']}">
</%block>

<%block name="title">
## Translators, used as page title
${_('Setup Completed')}
</%block>

<%
    exit_url = i18n_url('setup:exit', next=i18n_url('sys:root'))
%>

<h2><span class="icon icon-checkbox-marked-circle"></span> ${_('Settings are saved')}</h2>
<p class="image">
    <a href="${exit_url}">
        <img src="${i18n_url('sys:static', path='img/outernet_beta.png')}" alt="${_('Outernet is currently in beta')}">
    </a>
</p>
<p class="welcome">
    ${_('Welcome to Outernet')}
</p>
<p class="buttons">
    <a class="button confirm" href="${exit_url}">${_('Start using Outernet')}</a>
</p>
