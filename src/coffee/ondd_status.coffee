((window, $) ->

  CHECK_INTERVAL = 3000 # seconds

  statusContainer = $ '#signal-status'

  # Ignore if no container is found
  if not statusContainer.length
    return

  statusUrl = statusContainer.data 'url'

  updateStatus = () ->
    statusContainer.load statusUrl

  setInterval updateStatus, CHECK_INTERVAL

) this, this.jQuery
