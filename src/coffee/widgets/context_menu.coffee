((window, $) ->

  ExpandableBox = window.o.elements.ExpandableBox
  loadFailure = window.templates.modalLoadFailure

  class ContextMenu extends ExpandableBox
    constructor: (@id, @activator, @parent) ->
      @activator ?= '.o-contextbar-menu'

      super @id

      @children = @element.find '.o-context-menu-menuitem'
      @submenuLinks = @element.find '.o-context-menu-submenu-activator'
      @element.data 'context-menu', @
      thisMenu = @

      # Enumerate submenus and equip them with same ContextMenu wrapper
      @submenuLinks.each (idx, item) =>
        elem = $ item
        id = elem.attr 'id'
        targetId = elem.ariaProperty 'controls'
        elem.data 'context-menu', new ContextMenu targetId, id, @
        return

      # The refocusTimeout property holds a timer object that is reset each
      # time a menu item is focused. The timer is started by blur event on the
      # menu item, and if it times out, the whole menu is closed. This is a
      # workaround for the hidden navbar becoming unhidden when menu item is
      # focused by keyboard.
      @refocusTimeout = null

      @children.on 'focus', () =>
        if @refocusTimeout?
          clearTimeout @refocusTimeout
        if @collapsed
          @open()
        return

      @children.on 'blur', () =>
        @refocusTimeout = setTimeout () =>
          @close()
          return
        , 100
        return

      @children.updownNav()

      # Handle click events on the menu links
      @children.on 'click', (e) ->
        elem = $ @
        context = elem.data 'context'

        # If this is a direct link, just pass it through without further
        # processing.
        if context is 'direct'
          return

        e.preventDefault()

        if context is 'back'
          menu = elem.parents('.o-context-menu').data 'context-menu'
          menu.close()
          if menu.parent?
            menu.parent.open()
          return

        if context is 'submenu'
          menu = elem.data 'context-menu'
          thisMenu.close()
          menu.open()
          return

        url = elem.attr 'href'
        $.modalContent url
        return

    collapsible: 'self'
    activator: '.o-contextbar-menu'

    getInitialState: () ->
      @element.ariaProperty 'hidden' == 'true'

    onOpen: () ->
      @children.first().focus()
      return

    getActivator: () ->
      $ @activator

    updateAria: () ->
      @element.ariaProperty 'hidden', @collapsed
      return


  window.export 'ContextMenu', 'widgets', ContextMenu

) this, this.jQuery
