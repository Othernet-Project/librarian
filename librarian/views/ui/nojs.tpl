## The following defs are used to support collapsible UI elements where there 
## is no JavaScript support in the browser.

<%def name="comp_url(name)">
    <% state = request.params.get(name) == '1' %>
    % if state:
        ${i18n_path(request.path + h.del_qparam(name))}
    % else:
        ${i18n_path(request.path + h.set_qparam(**{name: '1'}))}
    % endif
</%def>

<%def name="cls_toggle(name, cls, flip=False)">
    <% cond = (request.params.get(name) == '1') ^ flip %>
    ${cls if cond else ''}
</%def>

<%def name="open_class(name)">
    ${self.cls_toggle(name, 'open')}
</%def>

<%def name="aria_exp(name)">
    % if request.params.get(name) == '1':
        aria-expanded="true"
    % else:
        aria-expanded="false"
    % endif
</%def>

<%def name="aria_hidden(name)">
    % if request.params.get(name) == '1':
        aria-hidden="false"
    % else:
        aria-hidden="true"
    % endif
</%def>
