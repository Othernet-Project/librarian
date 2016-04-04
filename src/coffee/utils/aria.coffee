(($) ->

  $.fn.ariaProperty = (prop, value) ->
    elem = $ @
    if value?
      elem.attr "aria-#{prop}", value.toString()
    else
      elem.attr "aria-#{prop}"

) this.jQuery
