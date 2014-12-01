% if meta.tags:
    % for name, tag_id in meta.tags.iteritems():
    <a class="tag" href="{{ i18n_path('/?t=%s' % tag_id) }}">{{ name }}</a>
    % end
% end
