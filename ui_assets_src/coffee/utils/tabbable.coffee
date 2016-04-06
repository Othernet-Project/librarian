((window, $, templates) ->
  tabOpenedEvent = 'tab-opened'

  $.tabbableDefaults =
      activator: '.o-tab-handle-activator'
      panel: '.o-tab-panel'
      spinnerTemplate: templates.spinner
      errorTemplate: templates.loadFail


  $.fn.tabbableCloseAll = () ->
    elem = $ this
    options = elem.data 'tabbableOptions'
    if not options
      return
    {activator, panel} = options
    (elem.find panel + '.active')
      .removeClass('active')
      .ariaProperty('expanded', 'false')
    (elem.find activator + '.active')
      .removeClass('active')
    elem


  $.fn.tabbableOpenTab = (tabId, suppressEvent) ->
    elem = $ this
    options = elem.data 'tabbableOptions'
    tabs = elem.data 'tabbableTabs'
    if not options
      return
    {activator, panel} = tabs[tabId]
    activator.addClass 'active'
    panel.addClass 'active'
    panel.ariaProperty 'expanded', 'true'

    if not suppressEvent
      elem.trigger 'tabchange', [activator, panel]

    url = panel.data 'url'

    if not url
      return

    panel.html options.spinnerTemplate
    res = $.get url
    res.done (data) ->
      panel.html data
      $.event.trigger({
        type: tabOpenedEvent,
        tabId: tabId
      });

    res.fail () ->
      panel.html options.errorTemplate

    elem


  $.fn.tabable = (options) ->
    options ?= {}
    options = $.extend {}, $.tabbableDefaults, options

    {activator, panel, onChange} = options
    elem = $ this

    elem.data 'tabbableOptions', options
    elem.data 'tabbableTabs', tabs = {}

    # Cache all panels
    (elem.find activator).each () ->
      act = $ this
      href = act.attr 'href'
      id = href.replace '#', ''
      panel = elem.find href
      tabs[id] =
        activator: act
        panel: panel
      return

    tabs = null  # Remove refrence to object to prevent leaks

    elem.on 'focus', activator, (e) ->
      elem.trigger 'activator-focus'

    elem.on 'click', activator, (e) ->
      e.preventDefault()
      tabId = (($ this).attr 'href').replace '#', ''
      elem.tabbableCloseAll()
      elem.tabbableOpenTab tabId

    elem

) this, this.jQuery, this.templates
