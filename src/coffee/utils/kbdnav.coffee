((window, $) ->

  # Adds keyboard navigation with up and down arrows
  $.fn.updownNav = (selector, skip) ->
    elem = $ @
    selector ?= 'a'
    skip ?= '.disabled'

    elem.on 'keyup', (e) ->
      elem = $ @
      switch e.which
        when 38
          elem.prevAll("#{selector}:not(#{skip})").first().focus()
        when 40
          elem.nextAll("#{selector}:not(#{skip})").first().focus()

) this, this.jQuery
