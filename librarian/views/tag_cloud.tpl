<%inherit file='base.tpl'/>
<%namespace name='tcloud' file='_tag_cloud.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Tag cloud')}
</%block>

${tcloud.body()}
