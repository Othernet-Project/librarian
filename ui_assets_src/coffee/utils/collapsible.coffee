((window, $) ->

  CLICKABLE_TARGET = 42
  RETURN = 13
  SPACE = 32
  ESC = 27

  win = $ window

  $.collapsibleDefaults =
      button: '.o-collapsible-section-title'
      collapsibleArea: '.o-collapsible-section-panel'
      collapsibleSection: '.o-collapsible-section'
      collapseClass: 'o-collapsed'


  $.fn.collapsible = (options) ->
    elem = $ this
    options ?= {}
    options = $.extend options, $.collapsibleDefaults
    {button, collapsibleArea, collapsibleSection, collapseClass} = options

    # The default stylesheet assigns a 'large-enough' max-height to uncollapsed
    # variant of the section. As this height does not exactly match the actual
    # height of uncollapsed section, the animation isn't smooth. Here we go
    # through all panels, get their height, and adjust the max-height of an
    # uncollapsed variant.
    remax = () ->
      section = $ this
      panel = section.find collapsibleArea
      totalHeight = panel.outerHeight()
      section.css 'max-height', totalHeight + CLICKABLE_TARGET
      section

    expand = (panel) ->
      section = panel.parents collapsibleSection
      button = section.find button
      section.addClass collapseClass
      panel.ariaProperty 'hidden', 'true'
      button.focus()

    collapsibleSections = elem.find collapsibleSection
    collapsibleSections.each () ->
      section = remax.call this
      section.data 'collapsible-parent', elem
      section.on 'remax', remax
      win.on 'resize', () =>
        remax.call this

    onclick = (e) ->
      e.preventDefault()
      clicked = $ e.target
      section = clicked.parents collapsibleSection
      panel = section.find collapsibleArea
      section.toggleClass collapseClass
      collapsed = section.hasClass collapseClass
      panel.ariaProperty 'hidden', if collapsed then 'true' else 'false'
      panel.focus()

    elem.on 'click', button, onclick

    # Inside the panel itself, we handle the Escape key to collapse the panel
    # and focus the button.
    elem.on 'keydown', collapsibleSection, (e) ->
      if e.which isnt ESC
        return
      panel = $ e.target
      section = panel.parents collapsibleSection
      button = section.find button
      section.addClass collapseClass
      panel.ariaProperty 'hidden', 'true'
      button.focus()

    elem

) this, this.jQuery
