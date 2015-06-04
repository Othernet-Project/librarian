<%inherit file="base.tpl"/>
<%namespace name="simple_pager" file="_simple_pager.tpl"/>
<%namespace name="list_controls" file="_list_controls.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Updates')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Updates')}
</%block>

% if nzipballs:
<div class="dash-updates content-archive dash-section">
    <div class="stat count">
    <span class="number">${nzipballs}</span>
    ## Translators, appears on updates page as a label, preceded by update count in big letter
    <span class="label">${ngettext('update available', 'updates available', nzipballs)}</span>
    </div>

    <div class="stat space">
    <span class="number">${last_zip.strftime('%m-%d')}</span>
    ## Translators, appears on updates page as a label, preceded by date of update in big letter
    <span class="label">${_('last update')}</span>
    </div>
</div>
% endif


<div class="inner">
    <div class="controls">
        <form id="pager" class="pager controls">
            ${h.vselect('lang', SELECT_LANGS, lang)}<button ## NOTE: keep together
            ## Translators, used as label for language filter button
                class="fake-go">${_('filter')}</button>
            ${simple_pager.body()}
        </form>
    </div>

    <form method="POST">
    % if metadata:
        ${list_controls.body()}
    % endif

    <table class="downloads-list">
        <thead>
            <tr>
            ## Translators, used as table header, above checkbox for selecting updates for import
            <th class="downloads-selection"><span class="icon">${_('select')}</span></th>
            ## Translators, used as table header, content title
            <th>${_('title')}</th>
            ## Translators, used as table header, broadcast date
            <th class="do">${_('broadcast')}</th>
            ## Translators, used as table header, download date
            <th class="do">${_('downloaded')}</th>
            ## Translators, used as table header, download language
            <th class="do">${_('language')}</th>
            </tr>
        </thead>
        <tbody>
            % if metadata:
                % for meta in metadata:
                <tr class="data">
                    <td class="downloads-selection">
                        <input id="check-${meta['md5']}" type="checkbox" name="selection" value="${meta['md5']}"${' checked' if selection else ''}>
                    </td>
                    <td class="downloads-title">
                        <p><label for="check-${meta['md5']}"><span${th.i18n_attrs(meta.lang)}>${meta['title'] | h}</span></label></p>
                        % if meta.get('replaces_title'):
                        <p class="downloads-replaces">
                        ${_('replaces:')}
                        <a href="${i18n_url('content:reader', content_id=meta['replaces'])}">
                            ${meta['replaces_title'] | h}
                        </a>
                        </p>
                        % endif
                    </td>
                    <td class="downloads-timestamp do">${h.strft(meta['timestamp'], '%m-%d')}</td>
                    <td class="downloads-ftimestamp do">${meta['ftimestamp'].strftime('%m-%d')}</td>
                    <td class="downloads-language do">${th.lang_name_safe(meta.get('language'))}</td>
                </tr>
                % endfor
            % else:
                <tr>
                    <td class="empty" colspan="5">
                    % if lang['lang']:
                    ## Translators, note that appears in table on updates page when there is no new downloaded content for a given language
                    ${_("Language filter for '%(lang)s' is active. Click %(link)s to see all updates") % {'lang': th.lang_name_safe(lang['lang']), 'link': '<a href="%(path)s">%(label)s</a>' % {'path': i18n_url(request.path) + h.set_qparam(lang='').to_qs(), 'label': _('here')}}}
                    % else:
                    ## Translators, note that appears in table on updates page when there is no new downloaded content
                    ${_('There is no new content')}
                    % endif
                </td>
                </tr>
            % endif
        </tbody>
    </table>

    % if metadata:
        ${list_controls.body()}
    % endif
    </form>
</div>

<%block name="extra_scripts">
<script src="/static/js/downloads.js"></script>
</%block>
