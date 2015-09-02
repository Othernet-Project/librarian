<%inherit file="_dashboard_section.tpl"/>
<%namespace name="settings_form" file="ondd/_settings_form.tpl"/>
<%namespace name="signal" file="ondd/_signal.tpl"/>
<%namespace name="file_list" file="ondd/_file_list.tpl"/>
<%namespace name="presets" file="ondd/_presets.tpl"/>

<div class="ondd-status">
    <div id="signal-status" class="signal-status" data-url="${i18n_url('ondd:status')}">
        ${signal.body()}
    </div>
    <div id="ondd-file-list" class="ondd-file-list" data-url="${i18n_url('ondd:files')}">
        ${file_list.body()}
    </div>
</div>

<div class="ondd-settings">
    ${settings_form.body()}
    ${presets.body()}
</div>

<script type="text/javascript" src="${assets['js/ondd']}"></script>
