<%inherit file="base.tpl"/>
<%namespace name="tags" file="_tags.tpl"/>
<%namespace name="tag_js_templates" file="_tag_js_templates.tpl"/>

<%block name="title">
${meta.title}
</%block>

<%block name="main">
<div class="reader">
    <div class="reader-frame">
        <iframe id="reader-main" class="reader-main" src="${i18n_url('content:file', content_id=meta.md5, filename=meta.entry_point)}"></iframe>
    </div>
    <div class="reader-meta data">
        <div class="inner">
            <p class="date">
            <strong>
                ${meta.timestamp.strftime('%Y-%m-%d')}
                % if meta.is_partner:
                / ${meta.partner}
                / <span class="special">${_('partner')}</span>
                % endif

                % if meta.is_sponsored:
                / ${meta.partner}
                / <span class="special">${_('sponsored')}</span>
                % endif

                % if meta.archive == 'core':
                / <span class="special">${_('core')}</span>
                % endif
            </strong>
            <a class="button small" href="${i18n_url('content:zipball', content_id=meta.md5)}">${_('Download')}</a>
            </p>
            <p class="licensing">${meta.human_license}</p>
            ${tags.tags(meta)}
        </div>
    </div>
</div>
</%block>

<%block name="script_templates">
${tag_js_templates.body()}
</%block>

<%block name="extra_scripts">
<script src="/static/js/reader.js"></script>
</%block>
