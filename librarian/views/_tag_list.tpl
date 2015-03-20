% setdefault('tag_id', None)
% if meta.tags:
    % for name, content_tag_id in meta.tags.iteritems():
    % if content_tag_id != tag_id:
        <a class="tag button small" href="{{ i18n_path(url('tags:list')) }}?tag={{ content_tag_id }}">{{ name }}</a>
    % else:
        <span class="tag tag-current button small">{{ name }}</span>
    % end
    % end
% end
