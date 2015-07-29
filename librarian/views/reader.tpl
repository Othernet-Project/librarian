<%inherit file="base.tpl"/>
<%namespace name="tags" file="_tags.tpl"/>
<%namespace name="tag_js_templates" file="_tag_js_templates.tpl"/>

<%block name="title">
${meta.title}
</%block>

<%block name="main">
<div class="reader">
    <div class="reader-frame">
        <iframe id="reader-main" class="reader-main" src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=file_path)}" data-keep-formatting="${meta.keep_formatting}"></iframe>
    </div>
    <div class="reader-meta data">
        <div class="inner">
            <p class="date">
            ## Translators, attribution line appearing in the content list
            <p class="attrib">
            ## Translators, used in place of publisher name if publsiher name is not known
            <% publisher = meta.publisher or _('unknown publisher') %>
            ${_('%(date)s by %(publisher)s.') % dict(date=meta.timestamp.strftime('%Y-%m-%d'), publisher=publisher)}
            ${th.readable_license(meta.license)}
            </p>
        </div>
    </div>
</div>
</%block>

<%block name="script_templates">
<script id="readerCssPatch" type="text/template">
    <link rel="stylesheet" type="text/css" href="${assets['css/content']}" />
</script>
</%block>

<%block name="extra_scripts">
<script src="${assets['js/reader']}"></script>
</%block>
