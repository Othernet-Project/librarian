<%inherit file="base.tpl"/>
<%namespace name="tags" file="_tags.tpl"/>
<%namespace name="tag_js_templates" file="_tag_js_templates.tpl"/>

<%block name="title">
${meta.title}
</%block>

<%block name="main">
<div class="reader">
    <div class="reader-frame">
        <iframe id="reader-main" class="reader-main" src="${i18n_url('content:file', content_path=th.get_content_path(meta.md5), filename=file_path)}" data-keep-formatting="${meta.keep_formatting}"></iframe>
    </div>
    <div class="reader-meta data">
        <div class="inner">
            <p class="date">
            <strong>
                ${meta.timestamp.strftime('%Y-%m-%d')}
                % if meta.is_partner:
                / ${meta.publisher}
                / <span class="special">${_('partner')}</span>
                % endif

                % if meta.is_sponsored:
                / ${meta.publisher}
                / <span class="special">${_('sponsored')}</span>
                % endif

                % if meta.archive == 'core':
                / <span class="special">${_('core')}</span>
                % endif
            </strong>
            <a class="button small" href="${i18n_url('content:zipball', content_id=meta.md5)}">${_('Download')}</a>
            </p>
            <p class="licensing">${readable_license(meta.license)}</p>
            ${tags.tags(meta)}
        </div>
    </div>
</div>
</%block>

<%block name="script_templates">
${tag_js_templates.body()}
<script id="readerCssPatch" type="text/template">
    <link rel="stylesheet" type="text/css" href="${th.static_url('sys:static', path='css/content.css')}" />
</script>

</%block>

<%block name="extra_scripts">
<script src="${th.static_url('sys:static', path='js/reader.js')}"></script>
</%block>
