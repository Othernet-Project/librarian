<!doctype html>

<html lang="${request.locale}"${' dir="rtl"' if is_rtl == True else ''}>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        ## Translators, used in page title
        <title><%block name="title">Outernet</%block> :: ${_('Librarian')} v${app_version}</title>
        <link rel="stylesheet" href="${url('sys:static', path="css/%s.css" %  style)}">
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
        % if redirect is not UNDEFINED:
        <meta http-equiv="refresh" content="5; url=${redirect}">
        % endif
    </head>
    <body>
        <header>
            <div id="toolbar" class="toolbar">
                <% icon = '<span class="icon"></span>' %>
                ## Translators, used main navigation menu
                ${h.link_other(icon + _('Library'), i18n_path(url('content:list')), request.original_path, h.SPAN, _class="archive navicon")}
                ## Translators, used main navigation menu
                ${h.link_other(icon + _('Files'), i18n_path(url('files:list')), request.original_path, h.SPAN, _class="files navicon")}
                ## Translators, used main navigation menu
                ${h.link_other(icon + _('Apps'), i18n_path(url('apps:list')), request.original_path, h.SPAN, _class="apps navicon")}
                ## Translators, used main navigation menu
                ${h.link_other(icon + _('Updates') + (' (%s)' % updates if updates > 0 else ''), i18n_path(url('downloads:list')), request.original_path, h.SPAN, _class="updates navicon" + (updates > 0 and ' notice' or ''))}
                ## Translators, used main navigation menu
                ${h.link_other(icon + _('Dashboard'), i18n_path(url('dashboard:main')), request.original_path, h.SPAN, _class="dashboard navicon")}
                ## Translators, used main navigation menu
                % if hasattr(request, 'user') and request.user.is_authenticated:
                ${h.link_other(icon + _('Log out'), i18n_path(url('auth:logout')) + '?next=' + request.fullpath, request.original_path, h.SPAN, _class="exit navicon")}
                % endif
            </div>
        </header>

        <div class="body">
        <%block name="main">
            <h1><%block name="heading"/></h1>
            <%block name="content">
                <div class="inner">
                    ${self.body(**context.kwargs)}
                </div>
            </%block>
        </%block>
        </div>

        <div id="languages" class="languages">
            % for locale, lang in languages:
                % if locale != request.locale:
                <a href="${i18n_path(locale=locale)}" dir="${dir(locale)}" lang="${locale}">${lang}</a>
                % else:
                <span class="current" dir="${dir(locale)}" lang="${locale}">${lang}</span>
                % endif
            % endfor
        </div>

        <div class="footer">
        <p class="logo"><img src="${url('sys:static', path='img/outernet_logo.png')}" alt="Outernet: Humanity's Public Library"></p>
        ## Translators, used in footer
        <p class="appver">${_('Librarian')} v${app_version}</p>
        <p class="copy">2014 Outernet Inc</p>
        </div>

        <%block name="script_templates"/>
        <script src="${url('sys:static', path='js/ui.js')}"></script>
        <%block name="extra_scripts"/>
    </body>
</html>
