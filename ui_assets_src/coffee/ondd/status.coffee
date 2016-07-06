((window, $) ->

  CHECK_INTERVAL = 3000 # seconds

  section = $ '#dashboard-ondd'
  statusContainer = null
  statusUrl = null

  updateStatus = () ->
    statusContainer.load statusUrl


  initPlugin = (e) ->
    statusContainer = $ '#signal-status'
    # Ignore if no container is found
    if not statusContainer.length
      return

    statusUrl = statusContainer.data 'url'
    setInterval updateStatus, CHECK_INTERVAL

  # in case of wizard-step, this must be invoked on page-load
  initPlugin()
  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery
