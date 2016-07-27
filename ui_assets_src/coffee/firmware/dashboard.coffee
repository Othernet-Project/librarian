((window, $, templates) ->

  partialSelector = "#firmware-update-container"
  container = $ "#dashboard-firmware-panel"
  section = container.parents '.o-collapsible-section'
  messages = {
    'firmwareUploading': null,
    'firmwareUpdating': null,
    'firmwareUpdateFailed': null,
    'firmwareWaitForReboot': null,
  }
  form = null
  iframe = null
  statusUrl = null

  TIMEOUT = 45000
  POLL_DELAY = 5000
  FAILED_STATUS = 'failed'


  setMessage = (msg) ->
    container.find('.firmware-messages').remove()
    container.prepend msg
    section.trigger 'remax'


  uploadStart = (e) ->
    button = container.find 'button'
    button.prop 'disabled', true
    setMessage messages.firmwareUploading
    return


  uploadDone = (e) ->
    partial = iframe.contents().find partialSelector
    container.html partial
    section.trigger 'remax'
    initPlugin()
    isSaved = form.data 'saved'
    if isSaved == true
      updateProgress()


  updateProgress = () ->
    setMessage messages.firmwareUpdating
    setTimeout pollProgress, POLL_DELAY


  pollProgress = () ->
    res = $.ajax { url: statusUrl, timeout: TIMEOUT }
    res.done (data) ->
      if data.status == FAILED_STATUS
        setMessage messages.firmwareUpdateFailed
        return
      setTimeout pollProgress, POLL_DELAY
    res.fail () ->
      setMessage messages.firmwareWaitForReboot
      return


  initPlugin = (e) ->
    for msgId of messages
      if messages[msgId] == null
        $("##{msgId}").loadTemplate()
        messages[msgId] = templates[msgId]
    form = container.find 'form'
    form.on 'submit', uploadStart
    iframe = container.find 'iframe'
    iframe.on 'load', uploadDone
    statusUrl = form.data 'status-url'


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates

