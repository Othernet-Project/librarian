((window, $) ->

  CHECK_INTERVAL = 3000

  filesContainer = $ '#ondd-file-list'
  section = filesContainer.parents '.o-collapsible-section'
  filesUrl = filesContainer.data 'url'

  updateFileList = () ->
    filesContainer.load filesUrl
    section.trigger 'remax'

  setInterval updateFileList, CHECK_INTERVAL

  return

) this, this.jQuery
