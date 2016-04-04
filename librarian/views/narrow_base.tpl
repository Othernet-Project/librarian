<%doc>
Narrow base template
====================

This template is used for pages that have a very simple interface (usually a 
single message or a single form). The template contains the same elements as 
base.tpl template (see base.tpl for more information) and all blocks present
in that template are overridable. The main difference is that this template
overrides the base's ``main`` block and adds a wrapper that is styled with 
limited page width.
</%doc>

<%inherit file="/base.tpl"/>

<%block name="main">
    <div class="o-narrow-panel">
        <%block name="narrow_main">
            ${self.body(**context.kwargs)}
        </%block>
    </div>
</%block>

