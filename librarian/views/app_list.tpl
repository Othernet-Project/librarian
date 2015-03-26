<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Apps')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Apps')}
</%block>

<ul class="app-list">
    % if apps:
        % for app in apps:
        <li id="app-${app.appid}" data-url="${app.url}" data-id="${app.appid}">
            <a id="link-${app.appid}" class="app-icon" href="${app.url}"><img src="${app.asset_url('icon.png')}"></a>
            <div class="app-details">
            <span class="app-title"><a href="${app.url}">${app.title}</a></span>
            <span class="app-description">${h.trunc(app.description, 50)}</span>
            ## Translators, refers to app author
            <span class="app-author">${_('author:')} ${app.author}</span>
            ## Translators, refers to app version
            <span class="app-version">${_('version:')} ${app.version}</span>
            </div>
            % if app.icon_behavior:
            <script src="${app.asset_url('behavior.js')}"></script>
            % endif
        </li>
        % endfor
    % else:
        ## Translators, message show in app listing when no apps are present.
        <p>${_('No apps found.')}</p>
    % endif
</ul>
