<%def name="prev_next_pager()">
    % if pager.has_prev:
    ## Translators, used in the pager 
    <a href="${i18n_path(request.path) + h.set_qparam(p=pager.page - 1).to_qs()}" class="pager-button prev"><span class="icon">${_('previous')}</span></a>
    % endif

    <span class="pages-count">
    ${_('Page %(current)s of %(total)s') % dict(current=pager.page, total=pager.pages)}
    </span>

    % if pager.has_next:
    ## Translators, used in the pager
    <a href="${i18n_path(request.path) + h.set_qparam(p=pager.page + 1).to_qs()}" class="pager-button next"><span class="icon">${_('next')}</span></a>
    % endif
</%def>

<%def name="pager_options()">
    ${h.form(method='GET')}
        % if pager.pages > 1:
        <label for="page">${_('page')}</label>
        ${h.vselect('p', pager.page_choices, vals, _id='page')}
        % endif
        ${h.vselect('pp', pager.per_page_choices, vals, id='per-page')}
        <label for="per-page">${_('per page')}</label>
        <button type="submit">${_('Reload')}</button>
    </form>
</%def>

<span class="pager-links">
    ${self.pager_options()}
    ${self.prev_next_pager()}
</span>
