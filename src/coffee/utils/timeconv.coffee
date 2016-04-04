((window, $) ->

  $.timeconv = (subtree) ->
    if subtree
      subtree = $ subtree
    else
      subtree = $ document
    time = $ 'time', subtree
    time.each () ->
      elem = $ this
      format = elem.data 'format'
      dtstr = elem.attr 'datetime'
      try
        dt = new Date dtstr
        if format == 'date'
          dt = dt.toLocaleDateString()
        else
          dt = dt.toLocaleString()
      catch e
        dt = dtstr
      elem.text dt.toString()

) this, this.jQuery
