((window, $, templates) ->

  FETCH_INTERVAL = 5000

  locale = (window.location.pathname.split '/')[1]
  stateUrl = "/#{locale}/state/"
  bindables = '*[data-bind]'
  state = {}


  class binder

    constructor: ->
      @data = undefined
      @targets = []

    bind: (element, attribute, path) ->
      # no possibility to provide multiple bindings for one element
      for existing in @targets
        if existing.element == element
          return
      # element is not in targets already, continue
      target = { element: element, attribute: attribute, path: path }
      @targets.push target

    updateDom: (data) ->
      for target in @targets
        if target.path
          extractor = (src, key) -> src[key]
          value = target.path.reduce extractor, data
        else
          value = data

        if target.attribute == 'text'
          target.element.text value
        else if target.attribute == 'html'
          target.element.html value
        else
          target.element.attr target.attribute, value 

    set: (data) ->
      @data = data 
      @updateDom data

    get: () ->
      @data


  getBinding = (key) ->
    instance = state[key]
    if !instance?
      instance = new binder()
      state[key] = instance
    instance


  update = (data) ->
    for key, value of data
      instance = getBinding key
      instance.set value


  fetch = () ->
    res = $.get stateUrl
    res.done (data) ->
      update data
      setTimeout fetch, FETCH_INTERVAL
    res.fail () ->
      console.log 'State synchronization failed.'
      # reschedule in case of errors as well
      setTimeout fetch, FETCH_INTERVAL


  bindTo = (element) ->
    target = element.data 'bind'
    # split text: data_source.nested.attr into it's components
    components = target.split /:(.+)/
    # split data_source.nested.attr into it's segments
    segments = components[1].split '.'
    key = segments[0].trim()
    instance = getBinding key
    instance.bind element, components[0], segments.slice(1)


  dataBind = () ->
    $(bindables).each () ->
      element = $ @
      bindTo element


  $(document).on 'data-bind', dataBind
  dataBind()
  setTimeout fetch, FETCH_INTERVAL

) this, this.jQuery, this.templates

