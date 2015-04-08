<%def name="cloud(tag_cloud, tag_id, tag=None)">
<p class="tag-cloud">
    % if tag:
    ## Translators, used as link table for a pseudo-tag that cancels tag-based filtering of content
    <a href="${base_path}" class="tag button small special">${_('everything')}</a>
    % endif
    % for t in tag_cloud:
        % if tag != t['name']:
            <a href="${base_path + h.set_qparam(tag=t['tag_id']).del_qparam('base_path').to_qs()}" class="tag button small">${t['name']} <span class="tag-count">${t['count']}</span></a>
        % else:
            <span class="tag tag-current button small">${t['name']} <span class="tag-count">${t['count']}</span></span>
        % endif
    % endfor
</p>
</%def>

${cloud(tag_cloud, tag_id, tag)}
