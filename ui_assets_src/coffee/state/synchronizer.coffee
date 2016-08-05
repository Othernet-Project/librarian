((window, $, templates) ->

  FETCH_INTERVAL = 5000

  locale = (window.location.pathname.split '/')[1]
  stateUrl = "/#{locale}/state/"
  window.state = {}
  registry = {}


  window.state.provider = (name) ->
    instance = registry[name]
    if !instance?
      instance = new provider name
      registry[name] = instance
      # add read-only property to state object instead of provider itself, so
      # the parens can be omitted when accessing them
      config = { get: instance.get }
      Object.defineProperty window.state, name, config
    instance


  class provider

    constructor: (name) ->
      @name = name
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
      # if a trapper was defined, callback with the name of the provider
      # being accessed
      if window.state.__trapper__?
        window.state.__trapper__ @name
      @data

    onchange: (callback) =>
      if $.inArray(callback, @callbacks) == -1
        @callbacks.push callback

    postprocessor: (fn, target=null) =>
      processor = (provider) ->
        data = provider.get()
        # pass the whole data to the processor as it might calculate it's
        # return value based on multiple values of the underlying structure
        processed = fn data

        if target == null
          # not a partial update, the return value of the post-processor
          # will overwrite the whole previous value in stealth mode, not
          # triggering the onchanged callbacks
          provider.set processed, true
          return

        # a partial update, the return value of the post-processor
        # will only update the specified target
        if typeof target is 'string'
          data[target] = processed
          return

        # target is an array of keys and/or indexes targeting a leaf of
        # the underlying structure
        copy = target.slice()
        while copy.length > 1
          data = data[copy.shift()]
        data[copy.shift()] = processed
        return

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

