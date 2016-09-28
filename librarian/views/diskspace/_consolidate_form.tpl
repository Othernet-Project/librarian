<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="forms" file="/ui/forms.tpl"/>

<%def name="button(storage_id, current_id)">
    <% 
        is_current = current_id == storage_id
        cls = None
        if error and is_current:
            cls = 'error'
        elif is_current:
            cls = 'diskspace-consolidation-started'
        if is_current:
            icon = 'spinning-loader'
            # Translators, this is used as a button to move all data to that
            # drive, while files are being moved
            label = _('Moving files here')
        else:
            icon = 'folder-right'
            # Translators, this is used as a button to move all data to that 
            # drive
            label = _('Move files here')
    %>
    <p class="diskspace-consolidate">
        <button 
            id="${storage_id}" 
            type="submit"
            name="storage_id" 
            value="${storage_id}"
            ${'disabled' if is_current else ''}
            ${'class="{}"'.format(cls) if cls else ''}>
            <span class="icon icon-${icon}"></span>
            <span>${label}</span>
        </button>
    </p>
</%def>

<%def name="storage_info(storage)">
    <%
        is_loop = storage.name.startswith('loop')
        if storage.is_loop:
            disk_type = 'internal'
            # Translators, used as description of storage device
            disk_type_label = _('internal storage')
        elif storage.bus != 'usb':
            # This is not an attached disk
            disk_type = 'internal'
            # Translators, used as description of storage device
            disk_type_label = _('internal storage')
        elif storage.is_removable:
            # This is an USB stick
            disk_type = 'usbstick'
            # Translators, used as description of storage device
            disk_type_label = _('removable storage')
        else:
            # Most likely USB-attached hard drive
            disk_type = 'usbdrive'
            # Translators, used as description of storage device
            disk_type_label = _('removable storage')
        disk_name = storage.humanized_name
    %>
    <span class="storage-icon icon icon-storage-${disk_type}"></span>
    <span class="storage-name storage-detail">
        ${disk_name}
    </span>
    <span class="storage-type storage-detail">
        ${disk_type_label}
    </span>
    <span class="storage-usage storage-detail">
        ${ui.progress_mini(storage.pct_used)}
        ## Translators, this is used next to disk space usage indicator in settings 
        ## panel. The {used}, {total}, and {free} are placeholders.
        ${_('{used} of {total} ({free} free)').format(
            used=h.hsize(storage.used),
            total=h.hsize(storage.total),
            free=h.hsize(storage.free))}
    </span>
</%def>

% if message:
    ${forms.form_message(message)}
% endif

% if error:
    ${forms.form_errors([error])}
% endif

<form action="${i18n_url('diskspace:consolidate')}" method="POST" data-state-url="${i18n_url('diskspace:consolidate_state')}" data-started="${active_storage_id or ''}">
    % for storage in storages:
        <div class="diskspace-storageinfo">
            ${self.storage_info(storage)}
        </div>
    % endfor
</form>

<script type="text/templates" id="diskspaceConsolidateSubmitError">
    ${forms.form_errors([_('Operation could not be started due to server error.')])}
</script>
