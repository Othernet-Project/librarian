<%inherit file="/narrow_base.tpl"/>
<%namespace name="consolidate_form" file="_consolidate_form.tpl"/>

<%block name="title">
${_('Move all files')}
</%block>

<h2>${_('Move all files')}</h2>

<p class="diskspace-consolidate-instructions">
    ${_('Choose a storage device to which you want to move all downloaded files. You cannot move files to a storage that does not have enough space to hold all files.')}
</p>

${consolidate_form.body()}

<%block name="extra_head">
    <link rel="stylesheet" href="${assets['css/diskspace']}">
</%block>
