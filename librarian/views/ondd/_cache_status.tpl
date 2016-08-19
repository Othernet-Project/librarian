<% 
cache_status = th.state.ondd['cache']
used_pct = round(float(cache_status['used']) / cache_status['total'] * 100, 2)
## Translators, shows the disk space status of the storage where ondd download cache is stored 
status_template = _("{percentage}% used ({amount} available)")
%>
% if cache_status['alert']:
    <p class="ondd-cache-alert">
        ${_("Download capacity is low and files may stop downloading soon. Free some disk space by moving files to an external storage device.")}
    </p>
% endif
## Translators, shows the disk space status of the storage where ondd download cache is stored 
<label>${_("Allocated download capacity")}</label>
<span class="ondd-cache-bar">
    <span class="ondd-cache-bar-indicator" style="width: ${used_pct}%" data-bind="style: {width: ondd.cache.usedPercentage + '%'}"></span>
</span>
<p class="ondd-cache-percentage-lcd" data-bind="text: ondd.cache.msgFree">
    ${status_template.format(percentage=used_pct, amount=h.hsize(cache_status['free']))}
</p>

<script type="text/template" id="onddCacheStatusMessage">${status_template}</script>

