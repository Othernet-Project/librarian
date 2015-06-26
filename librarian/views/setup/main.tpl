<!doctype html>

<html lang="${request.locale}"${' dir="rtl"' if th.is_rtl(request.locale) == True else ''}>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        ## Translators, used in page title
        <title><%block name="title">${_('Setup Wizard')}</%block> - Librarian v${app_version}</title>
        <link rel="stylesheet" href="${assets['css/wizard']}" />
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
        <%block name="extra_head"/>
    </head>
    <body class="step-${step_name}${' initial' if step_index == 1 else ''}">
        <%block name="header">
        <header class="menu">
            <div class="menu-subblock">
                <a class="logo" href="${i18n_url('content:list')}"><span lang="en">Outernet</span></a>
            </div>
            <div class="menu-block-right">
                <div class="steps menu-subblock">
                    <span class="steps">
                    % for i in range(1, step_count + 1):
                        % if i < step_index:
                        <span class="step previous"></span>
                        % elif i == step_index:
                        <span class="step current"></span>
                        % else:
                        <span class="step"></span>
                        % endif
                    % endfor
                    </span>
                </div>
            </div>
        </header>
        </%block>

        <div class="section body">
            <div class="h-bar">
            <%block name="step_title"/>
            <span class="wizard-steps">${_('Setup Wizard: Step %s of %s') % (step_index, step_count)}</span>
            <span class="step-logo step-${step_name}"></span>
            </div>
            <div class="setup-wizard full-page-form">
                ${h.form('POST', action=i18n_url('setup:main') + h.set_qparam(**{step_param: step_index}).to_qs())}
                    <%block name="step"/>
                    <p class="buttons">
                        % if step_index - 1 >= start_index:
                        <a class="button" href="${i18n_url('setup:main') + h.set_qparam(**{step_param: step_index - 1}).to_qs()}">${_('Back')}</a>
                        % endif
                        <button type="submit" name="action" value="next" class="primary">${_('Next')}</button>
                    </p>
                </form>
            </div>
        </div>

        <%block name="footer">
        <footer>
            <p class="logo"><span lang="en">Outernet</span>: ${_("Humanity's public library")}</p>
            <p class="progver" lang="en">Librarian</span> <span dir="ltr">v${app_version}</span></p>
            <p class="copyright">2014-2015 <span lang="en">Outernet Inc</span></p>
        </footer>
        </%block>

        <%block name="script_templates"/>
        <script src="${assets['js/ui']}"></script>
        <script src="${assets['js/setup']}"></script>
        <%block name="extra_scripts"/>
    </body>
</html>
