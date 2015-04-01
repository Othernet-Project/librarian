<%inherit file="_dashboard_section.tpl"/>
<%namespace name="space_info" file="diskspace/_space_info.tpl"/>

<p class="total">
${space_info.space(free, total)}
</p>

% if needed:
<p class="warning">
## Translators, this is a warning message appearing when disk space is below minimum
${_('You are running low on disk space.')}
## Translators, this is a button label that leads to page for library cleanup
<a href="${i18n_url('plugins:diskspace:cleanup')}">${_('Free some space now')}</a>
</p>
% endif

<div class="content-archive">
    <div class="stat count">
    <span class="number">${count}</span>
    ## Translators, used as a label in content library stats section on dashboard, preceded by count of items in the library
    <span class="label">${ngettext('item in the library', 'items in the library', count)}</span>
    </div>

    <div class="stat space">
    <span class="number">${h.hsize(used)}</span>
    ## Translators, used as a label in content library stats section on dashboard, preceded by library size in bytes, KB, MB, etc
    <span class="label">${_('used space')}</span>
    </div>
</div>
