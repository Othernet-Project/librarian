<%inherit file="/narrow_base.tpl"/>
<%namespace name="info" file="_info.tpl"/>

<%block name="title">
    ## Translators, used as page title on a page that shows file details
    <% metadata = entry.facets %>
    ${_('{title} details').format(title=metadata.get('title') or titlify(metadata['file']))}
</%block>

${info.body()}
