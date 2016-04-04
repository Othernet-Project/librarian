<%doc>
    This template module contains defs for creating classic pager widget. If 
    the current page is C, first page is F, last page is L, then the pager
    has the following structure:

        [PRE] [F] ... [C-2] [C-1] [C] [C+1] [C+2] ... [L] [NXT]

    PRE and NXT are aliases for C-1 and C+1 respectively, here special-cased as
    they are normally labelled as previous and next respectively (or 
    represented by left/right arrows and chevrons.

    This general layout has a few exceptional cases. 
    
    1. C == F (on first)

        [C] [C+1] [C+2] [C+3] [C+4] ... [L] [NXT]

    2. C == L (on last)

        [PRE] [F] ... [C-4] [C-3] [C-2] [C-1] [C]

    3. F == C-2 (

        [PRE] [C-2] [C-1] [C] [C+1] [C+2] ... [L] [NXT]
    
    4. F == C-1

        [PRE] [C-1] [C] [C+1] [C+2] [C+3] ... [L] [NXT]

    5. L == C+2

        [PRE] [F] ... [C-2] [C-1] [C] [C+1] [C+2] [NXT]

    6. L == [C+1]

        [PRE] [F] ... [C-3] [C-2] [C-1] [C] [C+1] [NXT]

    7. F == C-3

        [PRE] [F] [C-2] [C-1] [C] [C+1] [C+3] ... [L] [NXT]

    8. L == C+3

        [PRE] [F] ... [C-2] [C-1] [C] [C+1] [C+2] [L] [NXT]

</%doc>

<%def name="ellipsis()">
    <span class="o-pager-ellipsis">...</span>
</%def>

<%def name="page_link(page, link_class, label=None)">
    <% page_url = i18n_path(request.path + h.set_qparam(p=page).to_qs()) %>
    <a href="${page_url}" class="o-pager-control o-pager-${link_class}">
        <span class="o-pager-label">${label or page}</span>
    </a>
</%def>

<%def name="pager_links(pager_obj, prev_label, next_label)">
    <% 
    c = pager_obj.page
    f = 1
    l = pager_obj.pages

    if l == 1:
        return ''

    show_prev = c > 1
    show_next = c < l
    first_in_group = max(f, c - 2)
    last_in_group = min(l, first_in_group + 4)
    pages_in_group = last_in_group - first_in_group
    if pages_in_group < 4:
        first_in_group = max(f, last_in_group - 4)
    show_f = last_in_group - 5 >= f
    show_l = first_in_group + 4 < l
    show_ellip_f = f < c - 3
    show_ellip_l = l > c + 3
    %>
    %if show_prev:
        ${self.page_link(c - 1, 'prev', prev_label)}
    % endif
    % if show_f:
        ${self.page_link(f, 'first')}
    % endif
    % if show_ellip_f:
        ${self.ellipsis()}
    % endif
    % for p in range(first_in_group, last_in_group + 1):
        % if p == c:
            <span class="o-pager-control o-pager-current">${p}</span>
        % else:
            ${self.page_link(p, 'page')}
        % endif
    % endfor
    % if show_ellip_l:
        ${self.ellipsis()}
    % endif
    % if show_l:
        ${self.page_link(l, 'last')}
    % endif
    % if show_next:
        ${self.page_link(c + 1, 'next', next_label)}
    % endif
</%def>



