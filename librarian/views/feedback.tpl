<%inherit file="base.tpl"/>

<%block name="title">
${page_title}
</%block>

<div class="feedback ${status}">
    <span class="icon"></span>
    <p class="main">${page_title}</p>
    <p class="sub">${message}</p>
</div>
