((window, $, template) ->

  section = $ '#dashboard-ondd'
  cacheContainer = null
  messageTemplateId = "onddCacheStatusMessage"


  usedPercentage = (data) ->
    ( data.cache.used / data.cache.total * 100 ).toFixed 2


  hFree = (data) ->
    dahelpers.hsize data.cache.free


  msgFree = (data) ->
    templates[messageTemplateId]
      .replace('{percentage}', data.cache.usedPercentage)
      .replace('{amount}', data.cache.hFree)


  initPlugin = (e) ->
    $("##{messageTemplateId}").loadTemplate()

    provider = window.state.provider 'ondd'
    provider.postprocessor usedPercentage, ['cache', 'usedPercentage']
    provider.postprocessor hFree, ['cache', 'hFree']
    provider.postprocessor msgFree, ['cache', 'msgFree']


  section.on 'dashboard-plugin-loaded', initPlugin


) this, this.jQuery, this.template

