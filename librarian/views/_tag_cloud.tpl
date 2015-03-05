% setdefault('tag', None)
<p class="tag-cloud">
    % if tag:
    %# Translators, used as link table for a pseudo-tag that cancels tag-based filtering of content
    <a href="{{ i18n_path(url('content:list')) }}" class="tag button small special">{{ _('everything') }}</a>
    % end
    % for t in tag_cloud:
        % if tag != t['name']:
            <a href="{{ i18n_path(h.set_qparam(tag=t['tag_id'])) }}" class="tag button small">{{ t['name'] }} <span class="tag-count">{{ t['count'] }}</span></a>
        % else:
            <span class="tag tag-current button small">{{ t['name'] }} <span class="tag-count">{{ t['count'] }}</span></span>
        % end
    % end
</p>
