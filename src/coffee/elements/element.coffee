((window, $) ->

  class Element
    # Common class for all elements
    #
    # This class provides common utility functions for wrapping various
    # elements by `id` attribute. It is meant to be used by more complex DOM
    # structures that are used as widgets.

    constructor: (@id) ->
      @element = $ "##{@id}"

    elementClass: ''

    findChild: (cls) ->
      @element.find ".o-#{@elementClass}-#{cls}"

    updateAria: ()->
      false

  window.export 'Element', 'elements', Element

) this, this.jQuery
