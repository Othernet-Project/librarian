((window, $, templates) ->
  mainContainer = $ '#main-container'
  readerFrame = null

  applyOverride = (doc, style) ->
    override = readerFrame.data "override-#{style}"
    link = "<link rel=\"stylesheet\" href=\"#{override}\">"
    (doc.find 'head').append link
    return

  fullPatch = (doc) ->
    console.log 'full'
    override = readerFrame.data 'override-styling'
    (doc.find 'style').remove()
    (doc.find 'link[rel="stylesheet"]').remove()
    applyOverride doc, 'full'
    return

  partialPatch = (doc) ->
    applyOverride doc, 'partial'
    return

  getOverride = (doc) ->
    ((doc.find 'meta[name="outernet-styling"]').attr 'content')

  onFrameLoad = () ->
    doc = readerFrame.contents()
    override = getOverride doc
    if override == 'yes'
      fullPatch doc
    else if override == 'no'
      return
    else
      partialPatch doc

  setup = () ->
    if (mainContainer.data 'view') isnt 'html'
      return
    readerFrame = $ '#views-reader-frame'
    if not readerFrame.length
      setTimeout setup, 200
      return
    readerFrame.on 'load', () ->
      if (readerFrame.contents().prop 'readyState') is 'complete'
        onFrameLoad()

  window.onTabChange setup
  setup()

  return

) this, this.jQuery, this.templates
