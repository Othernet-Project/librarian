((window, $) ->
  'use strict'

  defaultOptions = {
    toggleSidebarOnSelect: true
  }

  Playlist = (container, options) ->
    @options = $.extend {}, defaultOptions, options
    @items = container.find(@options.itemSelector)
    @items.on 'click', 'a', @onSelect.bind(@)
    current = container.find(@options.currentItemSelector).first()
    if current.length
      @currentIndex = current.index()
    else
      @currentIndex = 0
    @setCurrent(@currentIndex)
    return

  Playlist:: = {
    setCurrent: (index) ->
      previous = @items.eq @currentIndex
      @currentIndex = index
      current = @items.eq index
      current.siblings().removeClass(@options['currentItemClass'])
      current.addClass(@options['currentItemClass'])
      @options.setCurrent?(current, previous)
      return

    length: () ->
      @items.length

    moveTo: (index) ->
      if index < 0 or index >= @length()
        return
      @setCurrent(index)
      ($ window).trigger 'playlist-updated'
      return

    next: () ->
      index = (@currentIndex + 1) % @length()
      @moveTo(index)
      return

    previous: () ->
      index = (@length() + @currentIndex - 1) % @length()
      @moveTo(index)
      return

    onSelect: (e) ->
      e.preventDefault()
      e.stopPropagation()
      item = $(e.target).closest(@options['itemSelector'])
      index = @items.index item
      @moveTo index
      toggle = @options.toggleSidebarOnSelect
      winW = ($ window).outerWidth()
      if (winW < 740 and toggle is 'narrow') or toggle is yes
        ($ window).trigger 'views-sidebar-toggle'
      return
  }

  window.Playlist = Playlist
  return

) this, this.jQuery
