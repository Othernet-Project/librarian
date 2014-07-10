% rebase('base.tpl', title=_('Dashboard'))
<h1>{{ _('Dashboard') }}</h1>

<div class="diskspace dash-section">
    <h2>Disk space</h2>
    <p class="spool">
    % include('_space_info', label=_('download directory'), space=spool)
    </p>
    <p class="content">
    % include('_space_info', label=_('content archive'), space=content)
    </p>
    <p class="total">
    % include('_space_info', label=_('total space'), space=total)
    </p>
</div>


