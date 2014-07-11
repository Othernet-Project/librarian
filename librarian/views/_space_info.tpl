<span class="label">{{ label }} ({{ h.hsize(space[0]) }} {{ _('free') }})</span>
% pct = round(space[0] / space[1] * 100, 1)
<span class="all{{ ' low' if pct <= 10 else '' }}">
<span class="free" style="width:{{ pct }}%"}>{{ pct }}%</span>
</span>
