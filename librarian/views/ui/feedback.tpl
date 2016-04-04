<%inherit file="/narrow_base.tpl"/>

<%block name="title">
${page_title}
</%block>

<% 
    if status == 'success':
        icon = 'ok-outline'
    else:
        icon = 'no-outline'
%>
<div class="feedback feedback-${status}">
    <div class="feedback-icon">
        <span class="icon icon-${icon}"></span>
    </div>
    <p class="feedback-main">${message}</p>
    <% link = '<a href="{url}">{target}</a>'.format(url=aesc(redirect_url), target=esc(redirect_target)) %>
    <p class="feedback-sub">${_("You'll be taken to {target} in {seconds} seconds.").format(seconds=REDIRECT_DELAY, target=link)}</p>
</div>
