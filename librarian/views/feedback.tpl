<%inherit file="base.tpl"/>

<%block name="title">
${page_title}
</%block>

<div class="feedback ${status}">
    <span class="icon"></span>
    <p class="main">${main_message}</p>
    <p class="sub">${sub_message}</p>
</div>
