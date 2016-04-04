((window, $, templates) ->

  setupTabs = () ->
    tabControls = $ templates.playlistTabs
    sidebar = $ '#views-sidebar'
    sidebar.addClass 'with-tabs'
    sidebar.prepend tabControls

    tabControls.on 'click', 'a', (e) ->
      e.preventDefault()
      activateTab this

    (tabControls.find 'a').first()


  activateTab = (button) ->
    ($ '.playlist-section-open').removeClass 'playlist-section-open'
    ($ '.playlist-tabs .active').removeClass 'active'
    button = $ button
    button.addClass 'active'
    href = button.attr 'href'
    ($ href).addClass 'playlist-section-open'

  if templates.playlistTabs?
    firstTab = setupTabs()
    activateTab firstTab

) this, this.jQuery, this.templates
