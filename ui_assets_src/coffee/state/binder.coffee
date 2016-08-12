((window, $, templates) ->

  bindables = '*[data-bind]'
  bindings = {}
  bindingIds = 0


  safeEval = (expression, context) ->
    body = "with(context) { return #{expression}; }"
    fn = new Function 'context', body
    fn context


  class binder

    constructor: (element, provider, expression) ->
      @element = element
      @provider = provider
      @expression = expression
      @provider.onchange @updateDom

    setAttribute: (attribute, value) =>
      if attribute == 'text'
        @element.text value
      else if attribute == 'html'
        @element.html value
      else if attribute == 'style'
        @element.css value
      else
        @element.attr attribute, value

    updateDom: (provider) =>
      resolved = safeEval @expression, window.state
      for attr, value of resolved
        @setAttribute attr, value


  catchProvider = (expression) ->
    # find the name of the provider being accessed in the expression
    accessed = []

    collector = (name) ->
      if accessed.indexOf name == -1
        accessed.push name

    # set up trap
    window.state.__trapper__ = collector
    try
      safeEval expression, window.state
    catch e
      if e instanceof ReferenceError
        name = e.message.split(' ')[0]
        accessed.push name

    # clear trap
    window.state.__trapper__ = null

    # accessed should contain the accessed provider either by trapping the
    # exception and extracting the name of the local that was not found, or
    # through the callback on the state object which fires when a getter is
    # invoked on `window.state`
    if accessed.length != 1
      throw new Error "Either none or multiple providers were trapped."

    return accessed[0]


  bindTo = (element, bindingId) ->
    target = element.data 'bind'
    expression = "{#{target}}"
    # extract the provider name from an expression using the trapper mechanism
    providerName = catchProvider expression
    provider = window.state.provider providerName
    instance = new binder(element, provider, expression)
    bindings[bindingId] = instance


  dataBind = () ->
    $(bindables).each () ->
      element = $ @
      if !(element.data 'binding-id')?
        element.data 'binding-id', ++bindingIds
        bindTo element, bindingIds


  $(document).on 'data-bind', dataBind
  dataBind()

) this, this.jQuery, this.templates

