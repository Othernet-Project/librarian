<%namespace name="forms" file="/ui/forms.tpl"/>

<iframe id="update-firmware" name="update-firmware" height="0" width="0" frameborder="0"></iframe>
<form id="update-firmware-form" action="${i18n_url('firmware:update')}" method="POST" enctype="multipart/form-data" target="update-firmware">
    % if success:
    ${forms.form_message(message)}
    % else:
    ${forms.form_errors([message]) if message else ''}
    % endif
    ${forms.form_errors([form.error]) if form.error else ''}
    ${forms.field(form.firmware)}
    ## Translators, button label that starts firmware update
    <button type="submit" class="primary">${_('Update firmware')}</button>
</form>

<script type="text/templates" id="firmwareUploadStart">
    <p>
        <span class="icon icon-spinning-loader"></span>
        <span>${_("Firmware upload in progress...")}</span>
    </p>
</script>
