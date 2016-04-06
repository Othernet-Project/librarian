((window, $) ->

  $.filteredDefaults =
    selector: 'a'
    input: '#filter'
    getText: (element) ->
      ($ element).text().toLowerCase()

  $.fn.filtered = (options) ->
    index = {}
    elem = $ this

    # Sort out the default options
    options ?= {}
    options = $.extend {}, $.filteredDefaults, options
    {selector, input, getText} = options

    # Grab the filtered elements
    filtered = elem.find selector

    # Index filtered items
    filtered.each () ->
      text = getText this
      index[text] = this

    # Attach event handler to input
    ($ input).on 'input', () ->
      val = ($ this).val().toLowerCase()
      if not val
        filtered.show()
        return
      filtered.hide()
      matches = []
      for key of index
        if (key.indexOf val) > -1
          matches.push index[key]
      ($ matches).show()
      return

    elem

) this, this.jQuery
