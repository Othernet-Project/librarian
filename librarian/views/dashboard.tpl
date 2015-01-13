%# Translators, used as page title
% rebase('base.tpl', title=_('Dashboard'))

%# Translators, used as page heading
<h1>{{ _('Dashboard') }}</h1>

% if zipballs:
<div class="dash-updates content-archive dash-section">
    <div class="stat count">
    <span class="number">{{ zipballs }}</span>
    %# Translators, appears on dashboard as a label, preceded by update count in big letter
    <span class="label">{{ ngettext('update available', 'updates available', zipballs) }}</span>
    </div>

    <div class="stat space">
    <span class="number">{{ last_zip.strftime('%m-%d') }}</span>
    %# Translators, appears on dashboard as a label, preceded by date of update in big letter
    <span class="label">{{ _('last update') }}</span>
    </div>
</div>
% end

<div class="inner">
    % for plugin in plugins:
    {{! plugin.render() }}
    % end
</div>

