((window, $, templates) ->

  FETCH_INTERVAL = 5000

  locale = (window.location.pathname.split '/')[1]
  stateUrl = "/#{locale}/state/"
  window.state = {}
  registry = {}


  window.state.get = (name) ->
    instance = registry[name]
    if !instance?
      instance = new provider()
      registry[name] = instance
      # add provider as a new property to state object, so the parens can
      # be omitted when accessing them
      config = { get: instance.get }
      Object.defineProperty window.state, name, config
    instance


  class provider

    constructor: ->
      @data = undefined
      @callbacks = []

    invokeCallbacks: () =>
      for fn in @callbacks
        fn @

    set: (data, stealth=false) =>
      @data = data 
      if not stealth
        @invokeCallbacks()

    get: () =>
      @data

    onchange: (callback) =>
      if $.inArray(callback, @callbacks) == -1
        @callbacks.push callback

    postprocess: (processors) =>
      for key, fn of processors
        processor = (provider) ->
          data = provider.get()
          if typeof data is 'object'
            data[key] = fn data
          else
            processed = fn data
            provider.set processed, true
        # add processor func to list of callbacks
        @onchange processor

  update = (data) ->
    for key, value of data
      instance = window.state.get key
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


  setTimeout fetch, FETCH_INTERVAL

) this, this.jQuery, this.templates

