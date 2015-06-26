<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Apps')}
</%block>

<ul class="app-list">
    % if apps:
        % for app in apps:
        <%
        app_url = i18n_url('apps:app', appid=app.appid)
        app_description = app.description(request.locale,
                                          request.default_locale,
        ## Translators, this is used when app doesn't provide a description
                                          _('No description provided'))
        %>
        <li id="app-${app.appid}" data-url="${app_url}" data-id="${app.appid}">
            <a id="link-${app.appid}" class="app-icon" href="${app_url}"><img src="${i18n_url('apps:asset', appid=app.appid, path='icon.png')}"></a>
            <div class="app-details">
            <span class="app-title"><a href="${app_url}">${app.title}</a></span>
            <span class="app-description">${h.trunc(app_description, 50)}</span>
            ## Translators, refers to app author
            <span class="app-author">${_('author:')} ${app.author}</span>
            ## Translators, refers to app version
            <span class="app-version">${_('version:')} ${app.version}</span>
            </div>
            % if app.icon_behavior:
            <script src="${i18n_url('apps:asset', appid=app.appid, path='behavior.js')}"></script>
            % endif
        </li>
        % endfor
    % else:
        ## Translators, message show in app listing when no apps are present.
        <p>${_('No apps found.')}</p>
    % endif
</ul>
