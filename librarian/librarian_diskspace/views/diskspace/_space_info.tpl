<%namespace name="widgets" file="../_widgets.tpl"/>

<%def name="space(free, total)">
<% pct = round((total - free) / float(total) * 100, 1) if total else 100 %>
${widgets.progress(
    ## Translators, used as label for storage space indicator
    _('Storage space'), 
    pct, 
    ## Translators, %(free)s and %(total)s are placeholders for disk space amount, please leave them as they are.
    _('%(free)s free of %(total)s') % {'free': h.hsize(free), 'total': h.hsize(total)}, pct)
}
</%def>

${space(free, total)}
