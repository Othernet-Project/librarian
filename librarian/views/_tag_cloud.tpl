% setdefault('tag', None)
<p class="tag-cloud">
    % if tag:
    %# Translators, used as link table for a pseudo-tag that cancels tag-based filtering of content
    <a href="{{ i18n_path('/') }}" class="tag">{{ _('everything') }}</a>
    % end
    % for t in tag_cloud:
        % if tag != t['name']:
            <a href="{{ i18n_path('/?t=%s' % t['tag_id']) }}" class="tag">{{ t['name'] }} <span class="tag-count">{{ t['count'] }}</span></a>
        % else:
            <span class="tag-current">{{ t['name'] }} <span class="tag-count">{{ t['count'] }}</span></span>
        % end
    % end
</p>
