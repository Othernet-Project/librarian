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
    <div class="diskspace dash-section">
        %# Translators, used as section heading on dashboard above disk space and similar information
        <h2>{{ _('Content library stats') }}</h2>
        % if spool != total:
            <p class="spool">
            %# Translators, %s is the amount of free space in bytes, KB, MB, etc.
            % include('_space_info', label=_('download directory (%s free)'), space=spool)
            </p>
        % end
        % if content != total:
            <p class="content">
            %# Translators, %s is the amount of free space in bytes, KB, MB, etc.
            % include('_space_info', label=_('content library (%s free)'), space=content)
            </p>
        % end
        <p class="total">
        %# Translators, %s is the amount of free space in bytes, KB, MB, etc.
        % include('_space_info', label=_('total space (%s free)'), space=total)
        </p>
        % if needed:
        <p class="warning">
        %# Translators, this is a warning message appearing when disk space is below 10%
        {{ _('You are running low on disk space.') }}
        %# Translators, this is a button label that leads to page for library cleanup
        <a href="{{ i18n_path('/cleanup/') }}">{{ _('Free some space now') }}</a>
        </p>
        % end

        <div class="content-archive">
            <div class="stat count">
            <span class="number">{{ count }}</span>
            %# Translators, used as a label in content library stats section on dashboard, preceded by count of items in the library
            <span class="label">{{ ngettext('item in the library', 'items in the library', count) }}</span>
            </div>

            <div class="stat space">
            <span class="number">{{ h.hsize(used) }}</span>
            %# Translators, used as a label in content library stats section on dashboard, preceded by library size in bytes, KB, MB, etc
            <span class="label">{{ _('used space') }}</span>
            </div>
        </div>
    </div>

    <div class="dash-logs dash-section">
        %# Translators, used as section heading on dashboard above disk space and similar information
        <h2>{{ _('Application logs') }}</h2>
        %# Translators, used as note in Application logs section
        <p>{{ _('Logs are shown in reverse chronological order') }}</p>
        <textarea>{{ logs }}</textarea>
    </div>
</div>

