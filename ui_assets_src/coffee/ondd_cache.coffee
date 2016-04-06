((window, $) ->

  CHECK_INTERVAL = 3000

  cacheContainer = $ '#ondd-cache-status'
  section = cacheContainer.parents '.o-collapsible-section'
  cacheUrl = cacheContainer.data 'url'

  updateCache = () ->
    cacheContainer.load cacheUrl
    section.trigger 'remax'

  setInterval updateCache, CHECK_INTERVAL

  return

) this, this.jQuery

