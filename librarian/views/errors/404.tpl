<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Page not found')}
</%block>

<%block name="error_title">
## Translators, used as error page heading
<span class="icon icon-alert-question"></span> ${_('Page not found')}
</%block>

<%block name="error_code">
404
</%block>

<%block name="error_message">
<p class="single">${_('The page you were looking for could not be found')}</p>
<% link = '<a href="{url}">{target}</a>'.format(url=redirect_url, target=_("main page")) %>
<p class="single">${_("You will be redirected to {target} in {seconds} seconds.").format(seconds=REDIRECT_DELAY, target=link)}</p>
</%block>
