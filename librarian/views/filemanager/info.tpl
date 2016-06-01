<%inherit file="/narrow_base.tpl"/>
<%namespace name="info" file="_info.tpl"/>

<%block name="title">
    ## Translators, used as page title on a page that shows file details
    <% metadata = entry.meta %>
    ${_('{title} details').format(title=metadata.get('title') or th.facets.titlify(metadata.name))}
</%block>

${info.body()}
