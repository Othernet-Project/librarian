% for meta in metadata:
<li class="data {{ meta.get('archive', 'unknown') }} {{ 'partner' if meta.is_partner else '' }} {{ 'sponsored' if meta.is_sponsored else '' }}" data-id="{{ meta.md5 }}">
    <p class="thumbnail">
    <a href="{{ i18n_path('/pages/%s' % meta.md5) }}">
    % if meta.images > 0 and meta.image:
        <img src="/covers/{{ meta.image }}">
    % else:
        <span class="thumb-placeholder"></span>
    % end
    </a>
    </p>

    <div class="details">
        <p class="label label-{{ meta.label }}">
            {{ meta.human_label }}
        </p>
        <h2 class="title">
            <a href="{{ i18n_path('/pages/%s' % meta.md5) }}">{{ meta.title }}</a>
        </h2>
        <p class="date">
            % if meta.partner:
                %# Translators, attribution (e.g., 'By Project Gutenberg')
                {{ u(_('by %s')) % meta.partner }},
            % end
            {{ meta.timestamp.strftime('%Y-%m-%d') }}
        </p>
        <p class="badges">
        % include('_badges')
        </p>
        % include('_tags')
        % include('_delete_button')
    </div>
</li>
% end
