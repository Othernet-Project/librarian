<%namespace name="forms" file="/ui/forms.tpl"/>

<iframe id="update-firmware" name="update-firmware" height="0" width="0" frameborder="0"></iframe>
<form id="update-firmware-form" action="${i18n_url('firmware:update')}" method="POST" enctype="multipart/form-data" target="update-firmware" data-status-url="${i18n_url('firmware:status')}" data-saved="${'true' if saved else 'false'}">
    ${forms.form_errors([message]) if message else ''}
    ${forms.form_errors([form.error]) if form.error else ''}
    ${forms.field(form.firmware)}
    ## Translators, button label that starts firmware update
    <button type="submit" class="primary">${_('Update firmware')}</button>
</form>

<script type="text/templates" id="firmwareUploading">
    <p class="firmware-messages">
        <span class="icon icon-spinning-loader"></span>
        <span>${_("Firmware upload in progress...")}</span>
    </p>
</script>
<script type="text/templates" id="firmwareUpdating">
    <p class="firmware-messages">
        <span class="icon icon-spinning-loader"></span>
        <span>${_("Updating firmware...")}</span>
    </p>
</script>
<script type="text/templates" id="firmwareWaitForReboot">
    <p class="firmware-messages">
        ${forms.form_message(_("Firmware installed, device is rebooting..."))}
    </p>
</script>
<script type="text/templates" id="firmwareUpdateFailed">
    <p class="firmware-messages">
        ${forms.form_errors([_("Firmware update failed.")])}
    </p>
</script>
