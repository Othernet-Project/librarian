<%namespace name="widgets" file="../_widgets.tpl"/>

<%def name="space(free, total)">
<% pct = round(free / total * 100, 1) if total != 0 else 100 %>
## Translators, %s is the amount of free space in bytes, KB, MB, etc.
${widgets.progress(_('Total space (%s free)') % h.hsize(free), pct)}
</%def>

${space(free, total)}
