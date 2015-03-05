<span class="pager-links">
    % if pager.page > 1:
    %# Translators, used in the pager
    <a href="{{ i18n_path(h.set_qparam(p=pager.page - 1)) }}" class="button prev">{{ _('previous') }}</a>
    % end

    {{! h.form(method='GET', _class='inline') }}
        % if pager.pages > 1:
        <label for="page">{{ _('page') }}</label>
        {{! h.vselect('p', pager.pager_choices, vals, _id='page') }}
        % end
        {{! h.vselect('pp', pager.per_page_choices, vals, id='per-page') }}
        <label for="per-page">{{ _('per page') }}</label>
        <button type="submit">{{ _('Reload') }}</button>
    </form>

    % if pager.page < pager.pages:
    %# Translators, used in the pager
    <a href="{{ i18n_path(h.set_qparam(p=pager.page + 1)) }}" class="button next">{{ _('next') }}</a>
    % end
</span>
