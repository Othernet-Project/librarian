<%def name="list(meta)">
% if meta.tags:
    % for name, content_tag_id in meta.tags.iteritems():
    % if content_tag_id != tag_id:
        <a class="tag button small" href="${base_path + h.set_qparam(tag=content_tag_id).del_qparam('base_path').to_qs()}">${name}</a>
    % else:
        <span class="tag tag-current button small">${name}</span>
    % endif
    % endfor
% endif
</%def>

${list(meta)}
