((window, $) ->

  PulldownMenubar = window.o.widgets.PulldownMenubar
  Statusbar = window.o.widgets.Statusbar
  ContextMenu = window.o.widgets.ContextMenu

  pdmb = new PulldownMenubar window.o.pageVars.menubarId
  scrl = new Statusbar window.o.pageVars.statusbarId
  ctxm = new ContextMenu window.o.pageVars.contextmenuId
  statusBarTabs = $('#' + window.o.pageVars.statusTabId)
  statusBarTabs.tabable()
  statusBarTabs.on 'activator-focus', (e)->
    scrl.open()
    return

  # Convert marked timestamps to local time as per browser's locale
  $.timeconv()

  # Since there's no good way to get DOM change events in order to apply time
  # format conversion, we monkey-patch jQuery's html() method in order to
  # perform time format conversion after the original method is done.
  origHtml = $.fn.html
  $.fn.html = () ->
    ret = origHtml.apply this, arguments
    if arguments.length
      $.timeconv(this)
    ret

  return

) this, this.jQuery
