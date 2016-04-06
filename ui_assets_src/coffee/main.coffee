((window, $, templates) ->
  'use strict'

  mainContainer = $ '#main-container'
  window.mainContainer = mainContainer

  activateSidebar = () ->
    if not templates.sidebarRetract?
      return
    ($ '#views-container').data 'has-sidebar', yes
    sidebar = $ '#views-sidebar'
    sidebar.addClass 'with-sidebar-handle'
    sidebar.prepend templates.sidebarRetract
    winWidth = ($ window).outerWidth()
    if winWidth < 740
      setTimeout () ->
        toggleSidebar()
      , 2000
    return


  toggleSidebar = () ->
    container = ($ '#views-container')
    if not container.data 'has-sidebar'
      return
    container.toggleClass 'sidebar-hidden'
    ($ window).trigger 'views-sidebar-toggled'
    return


  openSidebar = () ->
    ($ '#views-container').removeClass 'sidebar-hidden'
    ($ window).trigger 'views-sidebar-toggled'
    return


  closeSidebar = () ->
    ($ '#views-container').addClass 'sidebar-hidden'
    ($ window).trigger 'views-sidebar-toggled'
    return

  updateState = () ->
    mainContainer.data 'view', ($ '.views-tabs-tab-current').data 'view'

  window.loadContent = (url) ->
    res = $.get url
    res.done (data) ->
      mainContainer.html data
      (mainContainer.find 'a').first().focus()
      activateSidebar()
      updateState()
      window.triggerTabChange()
      return
    res.fail () ->
      # FIXME: Do not use alert, load a failure template into main view
      alert templates.alertLoadError
    return res

  mainContainer.on 'click', '.views-tabs-tab-link', (e) ->
    e.preventDefault()
    e.stopPropagation()

    elem = $ @
    url = elem.attr 'href'
    res = loadContent url
    res.done () ->
      window.history.pushState null, null, url
      window.triggerTabChange()
      return


  window.onTabChange = (func) ->
    window.mainContainer.on 'filemanager:tabchanged', func
    return


  window.triggerTabChange = () ->
    window.mainContainer.trigger 'filemanager:tabchanged'
    return


  window.changeLocation = (url) ->
    window.history.pushState null, null, url
    return


  $(window).on 'popstate', (e) ->
    loadContent window.location
    return

  updateState()
  activateSidebar()
  mainContainer.on 'click', '.views-sidebar-retract', toggleSidebar
  ($ window).on 'views-sidebar-toggle', toggleSidebar
  ($ window).on 'views-sidebar-close', closeSidebar
  ($ window).on 'views-sidebar-open', openSidebar


  return
) this, this.jQuery, this.templates

