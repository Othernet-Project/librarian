((window, $) ->

  CHECK_INTERVAL = 3000

  section = $ '#dashboard-ondd'
  cacheContainer = null
  cacheUrl = null


  updateCache = () ->
    cacheContainer.load cacheUrl
    section.trigger 'remax'


  initPlugin = (e) ->
    cacheContainer = section.find '#ondd-cache-status'
    cacheUrl = cacheContainer.data 'url'
    setInterval updateCache, CHECK_INTERVAL


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery

