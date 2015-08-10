<%inherit file="base.tpl"/>
<%namespace name="tags" file="_tags.tpl"/>
<%namespace name="tag_js_templates" file="_tag_js_templates.tpl"/>
<%namespace name='reader' file='${"content_readers/%s.tpl" % context["chosen_content_type"]}'/>

<%block name="title">
${meta.title}
</%block>

<%block name="extra_head">
<link rel="stylesheet" type="text/css" href="${assets.url}vendor/mediaelement/mediaelementplayer.css" />
</%block>

<%block name="main">
<div class="reader" data-content-type="${chosen_content_type}">
    <div class="reader-frame">
        ${reader.reader_display()}
    </div>
    <div class="reader-meta data">
        <div class="inner">
            ${reader.meta_display()}
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
