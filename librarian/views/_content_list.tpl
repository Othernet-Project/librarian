% for meta in metadata:
<li class="data {{ meta.get('archive', 'unknown') }} {{ 'partner' if meta.is_partner else '' }} {{ 'sponsored' if meta.is_sponsored else '' }}" data-id="{{ meta.md5 }}">
    <p class="thumbnail">
    <a href="{{ i18n_path(url('content:reader', content_id=meta.md5)) }}">
    % if meta.images > 0 and meta.image:
        <img class="thumb-image" src="{{ url('content:cover', path=meta.image) }}">
    % else:
        <span class="thumb-image thumb-placeholder"></span>
    % end
    </a>
    </p>

    <div class="details">
        <p class="label">
            <span class="label-archive label-{{ meta.label }}">
            {{ meta.human_label }}
            </span>
            <span class="datestamp">
            {{ meta.timestamp.strftime('%Y-%m-%d') }}
            </span>
        </p>
        <h2 class="title"{{! meta.i18n_attrs }}>
            <a href="{{ i18n_path(url('content:reader', content_id=meta.md5)) }}">{{ meta.title }}</a>
        </h2>
        % if meta.partner:
        <p class="attrib">
            %# Translators, attribution (e.g., 'By Project Gutenberg')
            {{ u(_('by %s')) % meta.partner }}
        </p>
        % end
        <p class="badges">
        % include('_badges')
        </p>
        % include('_tags')
        % include('_delete_button')
    </div>
</li>
% end
