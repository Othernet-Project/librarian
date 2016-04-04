((window, $) ->

  window.templates ?= {}

  $.fn.loadTemplate = (name) ->
    elem = $ this
    name = name or elem.attr 'id'
    text = elem.html().trim()
    window.templates[name] = text


  window.templates._collect = () ->
    $('script[type="text/template"]').each () ->
      $(this).loadTemplate()
    return

  window.templates._load = (id) ->
    $("##{id}").loadTemplate()

  window.templates._collect()


) this, this.jQuery
