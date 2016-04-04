((window, $) ->

  Element = window.o.elements.Element

  class ExpandableBox extends Element
    # Object for expandable boxes
    #
    # Expandable box will have an outer container, and two or more inner
    # containers. On of the inner containers must have a @collapsibleSection
    # class (defaults to '.o-collapsible') which can be expanded or collapsed
    # by toggling the 'open' class on the *outernet* container.
    #
    # It also expects the element to have at least one activator element which
    # has an @activator class (defaults to '.o-activator'). It will map a click
    # event handler to this activator so that it can expand or collapse the
    # collapsible element.
    #
    # This class also modifies the 'aria-expanded' attribute on the collapsible
    # element depending on the @collapsed state.
    #
    # ExpandableBox class also provides @onOpen and @onClose hooks to handle
    # open and close events respectively.

    constructor: (@id) ->
      super(@id)
      @collapsibleElement = @getCollapsible()
      @collapsed = @getInitialState()
      @activatorElement = @getActivator()
      @activatorElement.on 'click', (e) =>
        e.preventDefault()
        @toggle()

    collapsibleSection: '.o-collapsible'
    activator: '.o-activator'

    getInitialState: () ->
      @collapsibleElement.ariaProperty 'expanded' == 'false'

    getCollapsible: () ->
      if @collapsibleSection == 'self'
        @element
      else
        @element.find @collapsibleSection

    getActivator: () ->
      @element.find @activator

    toggle: (cond) ->
      cond = if cond? then cond else @collapsed
      @element.toggleClass 'open', cond
      @collapsed = not cond
      @updateAria()
      if @collapsed
        @onClose()
      else
        @onOpen()

    open: () ->
      @toggle true

    close: () ->
      @toggle false

    onOpen: () ->
      true

    onClose: () ->
      true

    updateAria: () ->
      @collapsibleElement.ariaProperty 'expanded', not @collapsed


  window.export 'ExpandableBox', 'elements', ExpandableBox

) this, this.jQuery
