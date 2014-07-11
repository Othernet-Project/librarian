% rebase('base.tpl', title=_('Dashboard'))
<h1>{{ _('Dashboard') }}</h1>

<div class="content-archive dash-section">
    <h2>{{ _('Content archive') }}</h2>

    <div class="stat count">
    <span class="number">{{ count }}</span>
    <span class="label">{{ ngettext('items in the archive', 'items in the archive', count) }}</span>
    </div>

    <div class="stat space">
    <span class="number">{{ h.hsize(used) }}</span>
    <span class="label">{{ _('used space') }}</span>
    </div>
</div>

<div class="diskspace dash-section">
    <h2>{{ _('Disk space') }}</h2>
    % if spool != total:
        <p class="spool">
        % include('_space_info', label=_('download directory'), space=spool)
        </p>
    % end
    % if content != total:
        <p class="content">
        % include('_space_info', label=_('content archive'), space=content)
        </p>
    % end
    <p class="total">
    % include('_space_info', label=_('total space'), space=total)
    </p>
</div>


