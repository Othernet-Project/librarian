% for meta in metadata:
<li class="data {{ meta.get('archive', 'unknown') }} {{ 'partner' if meta.is_partner else '' }} {{ 'sponsored' if meta.is_sponsored else '' }}" data-id="{{ meta.md5 }}">
    <h2 class="title">
        <a href="{{ i18n_path('/pages/%s/' % meta.md5) }}">
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
    <p class="tags" data-has-tags="{{ bool(meta.tags) }}">
    % include('_tag_list')
    </p>
    <form action="{{ i18n_path('/tag/%s' % meta.md5) }}" method="POST" class="tag-form">
        <p>
        <input type="text" name="tags" value="{{ ', '.join(meta.tags.keys()) }}">
        %# Translators, button label for a button that saves user tags for a piece of content
        <button class="small">{{ _('Save tags') }}</button>
        </p>
        <p class="help">
        %# Translators, note below the tag form (please note that it has to be the comma characters such as the one used in English language regardless of the interface language selected by user, so emphasize this where appropriate)
        {{ _('Separate tags with commas') }}<br>
        </p>
    </form>
</li>
% end
