<%inherit file="/base.tpl"/>
<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="main_view" file="_main.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Files')}
</%block>

<%block name="extra_head">
<link rel="stylesheet" type="text/css" href="${assets['css/filemanager']}" />
</%block>

<%block name="menubar_panel">
    <form id="files-multisearch" class="o-multisearch o-panel">
        <div class="o-panel">
            <label for="q" class="o-multisearch-label">
                ## Translators, used as label for search field, appears before the text box
                ${_('Search in folders:')}
            </label>
        </div>
        <div class="o-panel">
            ## Translators, used in file search box
            ${forms.text('q', _('Folder path or search keywords'), value=None if is_search else (esc(h.urlunquote(path)) if path != '.' else ''))}
        </div>
        <div class="o-panel">
            <button id="files-multisearch-button" type="submit" class="o-multisearch-button">
                ## Translators, used as button in file view address bar
                <span class="o-multisearch-button-label">${_('Start search')}</span>
                <span class="o-multisearch-button-icon icon"></span>
            </button>
        </div>
    </form>
</%block>

<%block name="main">
    <div class="o-main-inner" id="main-container">
        ${main_view.body()}
    </div>
</%block>

<%block name="extra_body">
    <script type="text/template" id="modalDialogCancelOnly">
        <%ui:modal_container id="dialog-cancel-only" close_button_label="_('Close')">
            <div class="o-modal-content o-modal-panel" role="document">
                <span class="o-modal-spinner">${_('Loading')}<span class="o-modal-spinner-loading-indicator">...</span></span>
            </div>
        </%ui:modal_container>
    </script>

    <script type="text/template" id="spinnerIcon">
        <span class="icon icon-spinning-loader"></span>
    </script>

    <script type="text/template" id="alertLoadError">
        ${_('Folder listing could not be loaded. Please try again in a few seconds.')}
    </script>
</%block>

<%block name="extra_scripts">
    <script type="text/javascript" src="${assets['js/filemanager']}"></script>
</%block>
