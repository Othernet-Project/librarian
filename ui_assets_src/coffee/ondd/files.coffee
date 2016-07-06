((window, $) ->

  CHECK_INTERVAL = 3000

  section = $ '#dashboard-ondd'
  filesContainer = null
  filesUrl = null


  updateFileList = () ->
    filesContainer.load filesUrl
    section.trigger 'remax'


  initPlugin = (e) ->
    setInterval updateFileList, CHECK_INTERVAL
    filesContainer = section.find '#ondd-file-list'
    filesUrl = filesContainer.data 'url'


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery
