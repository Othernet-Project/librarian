% for meta in metadata:
<li class="data {{ meta.get('archive', 'unknown') }} {{ 'partner' if meta.is_partner else '' }} {{ 'sponsored' if meta.is_sponsored else '' }}" data-id="{{ meta.md5 }}">
    <h2 class="title">
        <a href="{{ i18n_path('/pages/%s' % meta.md5) }}">
            % if meta.images > 0 and meta.image:
                <img src="/covers/{{ meta.image }}">
            % end
            <span>{{ meta.title }}</span>
        </a>
    </h2>
    <p class="date">
        {{ meta.timestamp.strftime('%Y-%m-%d') }}
    </p>
    <p class="badges">
    % include('_badges')
    </p>
    % include('_tags')
    % include('_delete_button')
</li>
% end
