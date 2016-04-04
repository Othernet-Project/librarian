((window, $) ->

  ExpandableBox = window.o.elements.ExpandableBox

  class PulldownMenubar extends ExpandableBox
    constructor: (@id) ->
      super(@id)

      # Stash references to relevant children
      @menu = @findChild 'menu'
      @firstNav = @menu.find("[role=\"menuitem\"]").first()

    elementClass: 'pulldown-menubar'

    onOpen: () ->
      @firstNav.focus()

  window.export 'PulldownMenubar', 'widgets', PulldownMenubar

) this, this.jQuery
