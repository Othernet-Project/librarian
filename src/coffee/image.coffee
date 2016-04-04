((window, $, templates) ->
  'use strict'

  LEFT_ARROW = 37
  RIGHT_ARROW = 39
  SPACE = 32


  $.fn.relpos = (x, y) ->
    # Position the child element relatively to its immediate parent such that
    # the position specified by x and y is in the middle of the parent. The x
    # and y coordinates are given as fraction (0.0 - 1.0) and they represent
    # the position within the element being centered.
    #
    # It is assumed that the element is absolutely positioned against the
    # parent.
    #
    el = $ this
    parent = el.parent()
    centerX = parent.outerWidth() / 2
    centerY = parent.outerHeight() / 2
    if el[0].nodeName is 'IMG'
      elemW = el[0].naturalWidth
      elemH = el[0].naturalHeight
    else
      elemW = el.outerWidth()
      elemH = el.outerHeight()
    elemXpos = x * elemW
    elemYpos = y * elemH
    left = centerX - elemXpos
    top = centerY - elemYpos
    el.css
      left: left + 'px'
      top: top + 'px'


  $.throttled = (fn, interval) ->
    # TODO: Move this somewhere so it's accessible to everyone
    interval ?= 200 #ms
    lastCall = 0
    () ->
      current = Date.now()
      if current - lastCall > interval
        lastCall = current
        fn.apply this, [].slice.call arguments, 0


  gallery =
    initialize: (@container) ->
      @currentImage = @container.find(
        '.gallery-current-image img').first()
      @imageMetadata = $ '#playlist-metadata'
      @prevHandle = $ '#gallery-control-previous'
      @nextHandle = $ '#gallery-control-next'
      @imageFrame = @currentImage.parent()

      @imageFrame.on 'click', '.zoomable', (e) =>
        if @currentImage.hasClass 'zoomed'
          @currentImage.removeClass 'zoomed'
          @prevHandle.show()
          @nextHandle.show()
          return

        @prevHandle.hide()
        @nextHandle.hide()
        # Get the relative coordinate of the click within the image
        {pageX, pageY} = e
        {left, top} = @currentImage.offset()
        width = @currentImage.width()
        height = @currentImage.height()
        xperc = (pageX - left) / width
        yperc = (pageY - top) / height
        # Get the position of the image top-left corner relative to container's
        # top left corner which causes the point within the image that was
        # clicked to be centered within the container.
        @currentImage.relpos xperc, yperc
        @currentImage.addClass 'zoomed'
        return

      # Move the zoomed image around while moving the mouse
      @currentImage.parent().on 'mousemove', $.throttled (e) =>
        if not @currentImage.hasClass 'zoomed'
          return
        {pageX, pageY} = e
        {left, top} = @imageFrame.offset()
        containerW = @imageFrame.outerWidth()
        containerH = @imageFrame.outerHeight()
        containerX = Math.min (Math.max pageX - left, 0), containerW
        containerY = Math.min (Math.max pageY - top, 0), containerH
        xperc = containerX / containerW
        yperc = containerY / containerH
        @currentImage.relpos xperc, yperc
        return
      , 50


      # Bind next/previous controls
      @prevHandle.on 'click', (e) =>
        e.preventDefault()
        e.stopPropagation()
        @previous()
        return
      @nextHandle.on 'click', (e) =>
        e.preventDefault()
        e.stopPropagation()
        @next()
        return

      # Make container focusable and focus it
      @container.attr 'tabindex', -1
      @container.focus()
      @container.on 'keydown', (e) =>
        if e.which in [RIGHT_ARROW, SPACE]
          @next()
        else if e.which is LEFT_ARROW
          @previous()

      currentItemClass = 'gallery-list-item-current'
      options = {
        itemSelector: '#playlist-list .gallery-list-item',
        currentItemClass: currentItemClass,
        currentItemSelector: '.' + currentItemClass,
        toggleSidebarOnSelect: 'narrow',
        setCurrent: (current, previous) =>
          @onSetCurrent(current, previous)
      }
      @playlist = new Playlist @container, options
      return

    makeZoomable: () ->
      frameW = @imageFrame.outerWidth()
      frameH = @imageFrame.outerHeight()
      imageW = @currentImage[0].naturalWidth
      imageH = @currentImage[0].naturalHeight
      isBig = imageW > frameW or imageH > frameH
      @currentImage.toggleClass 'zoomable', isBig
      return

    onSetCurrent: (current, previous) ->
      title = current.data 'title'
      imageUrl = current.data 'direct-url'
      metaUrl = current.data 'meta-url'
      @prevHandle.hide()
      @nextHandle.hide()
      @currentImage.removeClass 'zoomed'
      @currentImage.attr {
        'src': imageUrl
        'title': title
        'alt': title
      }
      @currentImage.on 'load', () =>
        @prevHandle.show()
        @nextHandle.show()
        @makeZoomable()
      @imageMetadata.load metaUrl
      previousUrl = previous.data('url')
      nextUrl = current.data('url')
      if previousUrl != nextUrl
        window.changeLocation nextUrl
      return

    next: () ->
      @playlist.next()
      @container.focus()
      return

    previous: () ->
      @playlist.previous()
      @container.focus()
      return


  prepareGallery = () ->
    galleryContainer = $ '#gallery-container'
    if not galleryContainer.length
      return
    gallery.initialize $ '#views-container'
    return

  $ prepareGallery
  window.onTabChange prepareGallery

  return
) this, this.jQuery
