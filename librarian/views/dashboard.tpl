% rebase('base.tpl', title=_('Dashboard'))
<div class="content-archive dash-section">
    <div class="stat count">
    <span class="number">{{ count }}</span>
    <span class="label">{{ ngettext('item in the archive', 'items in the archive', count) }}</span>
    </div>

    <div class="stat space">
    <span class="number">{{ h.hsize(used) }}</span>
    <span class="label">{{ _('used space') }}</span>
    </div>

    <div class="stat update">
    <span class="number">{{ last_updated.strftime('%m-%d') if last_updated else '?' }}</span>
    <span class="label">{{ _('last update') }}</span>
    </div>
</div>

<div class="favorites">
    <h2>{{ _('Favorite content') }}</h2>

    % if not favorites:
    <p>{{ _('You have not favorted any content yet') }}</p>
    % else:
    <ul>
        % for favorite in favorites:
        <li><a href="{{ i18n_path('/content/%s/' % favorite['md5']) }}">{{ favorite['title'] }}</a></li>
        % end
    </ul>
    <p><a href="{{ i18n_path('/favorites/') }}">{{ _('see all favorites') }} >></a></p>
    % end
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
    % if needed:
    <p class="warning">
    {{ _('You are running low on disk space.') }}
    <a href="{{ i18n_path('/cleanup/') }}">{{ _('Free some space now') }}</a>
    </p>
    % end
</div>


