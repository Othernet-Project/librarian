<%def name="space(free, total)">
<span class="label">
    ## Translators, %s is the amount of free space in bytes, KB, MB, etc.
    ${_('total space (%s free)') % h.hsize(free)}
</span>
<% pct = round(free / total * 100, 1) if total != 0 else 100 %>
<span class="all${' low' if pct <= 10 else ''}">
    <span class="free" style="width:${pct}%"}>${pct}%</span>
</span>
</%def>

${space(free, total)}
