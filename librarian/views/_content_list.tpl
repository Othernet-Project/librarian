<%namespace name='tags' file='_tags.tpl'/>
<%namespace name='delete_button' file='_delete_button.tpl'/>

% for meta in metadata:
<li class="data ${meta.get('archive', 'unknown')} ${'partner' if meta.is_partner else ''} ${'sponsored' if meta.is_sponsored else ''} ${'has-thumb' if meta.images else ''}" data-id="${meta.md5}" ${'style="background-image: url(\'{}\')"'.format(url('content:file', content_path=th.get_content_path(meta.md5), filename=meta.image)) if meta.images else ''}>
    <div class="details">
        <p class="label-archive label-${meta.label}">
        ${_(meta.label)}
        </p>
        <h2 class="title"${th.i18n_attrs(meta.lang)}>
            <a href="${i18n_url('content:reader', content_id=meta.md5)}">${meta.title | h}</a>
            % if th.is_authenticated():
            ${delete_button.button(meta=meta)}
            % endif
        </h2>
        ${tags.tags(meta)}
        <p class="attrib">
        ## Translators, used in place of publisher name if publsiher name is not known
        <% publisher = meta.publisher or _('unknown publisher') %>
        ## Translators, attribution line appearing in the content list
        ${_('%(date)s by %(publisher)s.') % dict(date=meta.timestamp.strftime('%Y-%m-%d'), publisher=publisher)}
        ${th.readable_license(meta.license)}
        </p>
    </div>
</li>
% endfor
