((window, $, templates) ->

  FETCH_INTERVAL = 5000

  locale = (window.location.pathname.split '/')[1]
  stateUrl = "/#{locale}/state/"
  window.state = {}


  window.state.get = (name) ->
    instance = window.state[name]
    if !instance?
      unwrapped = new provider()
      wrapper = () -> @get()
      instance = wrapper.bind unwrapped
      instance.__proto__ = unwrapped
      window.state[name] = instance
    instance


  class provider

    constructor: ->
      @data = undefined
      @callbacks = []

    invokeCallbacks: () =>
      for fn in @callbacks
        fn @

    set: (data) =>
      @data = data 
      @invokeCallbacks()

    get: () =>
      @data

    onchange: (callback) =>
      if $.inArray(callback, @callbacks) == -1
        @callbacks.push callback


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

