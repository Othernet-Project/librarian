<%inherit file="base.tpl"/>
<%namespace name="tag_js_templates" file="_tag_js_templates.tpl"/>
<%namespace name='reader' file='${"content_readers/%s.tpl" % context["chosen_content_type"]}'/>

<%block name="title">
${meta.title}
</%block>

<%block name="extra_head">
<link rel="stylesheet" type="text/css" href="${assets.url}vendor/mediaelement/mediaelementplayer.css" />
</%block>

<%block name="main">
<div class="reader ${chosen_content_type}" data-content-type="${chosen_content_type}">
    <div class="reader-frame reduced">
        ${reader.reader_display()}
    </div>
    <div class="reader-meta data expanded">
        <div class="inner">
            <div class="toggle"><span class="icon"></span></div>
            <div class="meta-container">
                ${reader.meta_display()}
            </div>
        </div>
    </div>
</div>
</%block>

<%block name="script_templates">
${tag_js_templates.body()}
<script id="readerCssPatch" type="text/template">
    <link rel="stylesheet" type="text/css" href="${assets['css/content']}" />
</script>
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${assets['js/reader']}"></script>
</%block>
