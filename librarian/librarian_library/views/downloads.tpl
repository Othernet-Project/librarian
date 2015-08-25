<%inherit file="base.tpl"/>
<%namespace name="simple_pager" file="_simple_pager.tpl"/>
<%namespace name="list_controls" file="_list_controls.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Updates')}
</%block>

% if nzipballs:
<div class="h-bar">
    <h2 class="stat count">
    <span class="number">${nzipballs}</span>
    ## Translators, appears on updates page as a label, preceded by update count in big letter
    <span class="label">${ngettext('update available', 'updates available', nzipballs)}</span>
    </h2>

    <div class="form actions">
        <form method="post">
            <button name="action" value="add_all" class="confirm primary">
                <span class="icon">${_('Add all to Library')}</span>
            </button>
            <button name="action" value="delete_all" class="delete">
                <span class="icon">${_('Discard all')}</span>
            </button>
        </form>
    </div>
</div>
% endif

<div class="filters">
    <div class="form langs">
        <form id="lang" class="downloads-langs">
            ${h.vselect('lang', th.download_languages(), lang)}
            ## Translators, used as label for language filter button
            <button class="fake-go">${_('Filter')}</button>
        </form>
    </div>
    <div class="form pager">
        ${simple_pager.prev_next_pager()}
    </div>
</div>

% if not metadata:
<div class="info">
    <p class="neutral">
        % if lang['lang']:
        ## Translators, note that appears in table on updates page when there is no new downloaded content for a given language
        ${_("Language filter for '%(lang)s' is active. Click %(link)s to see all updates") % {'lang': th.lang_name_safe(lang['lang']), 'link': '<a href="%(path)s">%(label)s</a>' % {'path': i18n_url(request.path) + h.set_qparam(lang='').to_qs(), 'label': _('here')}}}
        % else:
        ## Translators, note that appears in table on updates page when there is no new downloaded content
        ${_('There is no new content')}
        % endif
    </p>
</div>
% endif

% if metadata:
<ul class="downloads-list">
    % for meta in metadata:
    <li class="data">
        <h3
        class="downloads-title"><span${th.i18n_attrs(meta.lang)}>${meta['title'] | h}</span></h3>

        % if meta.get('replaces_title'):
        <p class="downloads-replaces">
        ## Translators, this appears in front of the title of a content that is being replaced by an updated copy
        ${_('replaces:')}
        <a href="${i18n_url('content:reader', content_id=meta['replaces'])}">
            ${meta['replaces_title'] | h}
        </a>
        </p>
        % endif

        <form method="POST" class="downloads-action">
            <input type="hidden" name="selection" value="${meta['md5']}">
            ## Translators, used as button label on updates page for adding marked content to library
            <button type="submit" name="action" value="add" class="confirm small">${_('Add to library')}</button>
            ## Translators, used as button label on updates page for permanently deleting all downloaded content
            <button type="submit" name="action" value="delete" class="delete small">${_('Discard')}</button>
        </form>

        <p class="downloads-ftimestamp do">
        <span class="label">${_('received on:')}</span> ${meta['ftimestamp'].strftime('%Y-%m-%d')}
        </p>

        <p class="downloads-language do">
        <span class="label">${_('language:')}</span> ${th.lang_name_safe(meta.get('language'))}
        </p>
    </li>
    % endfor
</ul>
% endif

<div class="bottom-pager">
${simple_pager.prev_next_pager()}
</div>
