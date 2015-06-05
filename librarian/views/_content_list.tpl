<%namespace name='tags' file='_tags.tpl'/>
<%namespace name='delete_button' file='_delete_button.tpl'/>

% for meta in metadata:
<li class="data ${meta.get('archive', 'unknown')} ${'partner' if meta.is_partner else ''} ${'sponsored' if meta.is_sponsored else ''}" data-id="${meta.md5}">
    <p class="thumbnail">
    <a href="${i18n_url('content:reader', content_id=meta.md5)}">
    % if meta.images > 0 and meta.image:
        <img class="thumb-image" src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta.image)}">
    % else:
        <span class="thumb-image thumb-placeholder"></span>
    % endif
    </a>
    </p>

    <div class="details">
        <p class="label">
            <span class="label-archive label-${meta.label}">
            ${_(meta.label)}
            </span>
            <span class="datestamp">
            ${meta.timestamp.strftime('%Y-%m-%d')}
            </span>
        </p>
        <h2 class="title"${th.i18n_attrs(meta.lang)}>
            <a href="${i18n_url('content:reader', content_id=meta.md5)}">${meta.title | h}</a>
        </h2>
        % if meta.publisher:
        <p class="attrib">
            ## Translators, attribution (e.g., 'By Project Gutenberg')
            ${unicode(_('by %s')) % meta.publisher | h}
        </p>
        % endif
        <p class="badges"></p>
        ${tags.tags(meta)}
        % if th.is_authenticated():
        ${delete_button.button(meta=meta)}
        % endif
    </div>
</li>
% endfor
