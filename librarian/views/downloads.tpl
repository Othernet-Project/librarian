%# Translators, used as page title
% rebase('base.tpl', title=_('Updates'))
%# Translators, used as page heading
<h1>{{ _('Updates') }}</h1>

% if nzipballs:
<div class="dash-updates content-archive dash-section">
    <div class="stat count">
    <span class="number">{{ nzipballs }}</span>
    %# Translators, appears on updates page as a label, preceded by update count in big letter
    <span class="label">{{ ngettext('update available', 'updates available', nzipballs) }}</span>
    </div>

    <div class="stat space">
    <span class="number">{{ last_zip.strftime('%m-%d') }}</span>
    %# Translators, appears on updates page as a label, preceded by date of update in big letter
    <span class="label">{{ _('last update') }}</span>
    </div>
</div>
% end


<div class="inner">
    <div class="controls">
    % include('_simple_pager')
    </div>

    <form method="POST">
    % if metadata:
    % include('_list_controls')
    % end

    <table class="downloads-list">
        <thead>
            <tr>
            %# Translators, used as table header, above checkbox for selecting updates for import
            <th class="downloads-selection"><span class="icon">{{ _('select') }}</span></th>
            %# Translators, used as table header, content title
            <th>{{ _('title') }}</th>
            %# Translators, used as table header, broadcast date
            <th class="do">{{ _('broadcast') }}</th>
            %# Translators, used as table header, download date
            <th class="do">{{ _('downloaded') }}</th>
            </tr>
        </thead>
        <tbody>
            % if metadata:
                % for meta in metadata:
                <tr class="data">
                    <td class="downloads-selection">
                        <input id="check-{{ meta['md5'] }}" type="checkbox" name="selection" value="{{ meta['md5'] }}"{{ selection and ' checked' or ''}}>
                    </td>
                    <td class="downloads-title"{{ ' rowspan="3"' if meta.get('replaces_title') else '' }}>
                        <p><label for="check-{{ meta['md5'] }}"><span{{! meta.i18n_attrs }}>{{ meta['title'] }}</span></label></p>
                        % if meta.get('replaces_title'):
                        <p class="downloads-replaces">{{ _('replaces:') }} <a href="{{ i18n_path(url('content:reader', content_id=meta['replaces'])) }}/">{{ meta['replaces_title'] }}</a></p>
                        % end
                    </td>
                    <td class="downloads-timestamp do">{{ h.strft(meta['timestamp'], '%m-%d') }}</td>
                    <td class="downloads-ftimestamp do">{{ meta['ftimestamp'].strftime('%m-%d') }}</td>
                </tr>
                % end
            % else:
                <tr>
                %# Translators, note that appears in table on updates page when there is no new downloaded content
                <td class="empty" colspan="4">{{ _('There is no new content') }}</td>
                </tr>
            % end
        </tbody>
    </table>

    % if metadata:
    % include('_list_controls')
    % end
    </form>
</div>

<script src="/static/js/jquery.js"></script>
<script src="/static/js/downloads.js"></script>
