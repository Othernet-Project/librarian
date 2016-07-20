((window, $, templates) ->

  partialSelector = "#firmware-update-container"
  container = $ "#dashboard-firmware-panel"
  section = container.parents '.o-collapsible-section'
  startMessageId = '#firmwareUploadStart'
  startMessage = null
  form = null
  iframe = null


  uploadStart = (e) ->
    button = container.find 'button'
    button.prop 'disabled', true
    container.prepend startMessage
    section.trigger 'remax'
    return


  uploadDone = (e) ->
    partial = iframe.contents().find partialSelector
    container.html partial
    section.trigger 'remax'
    initPlugin()


  initPlugin = (e) ->
    $(startMessageId).loadTemplate()
    startMessage = templates.firmwareUploadStart
    form = container.find 'form'
    form.on 'submit', uploadStart
    iframe = container.find 'iframe'
    iframe.on 'load', uploadDone


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates

