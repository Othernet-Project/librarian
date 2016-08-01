((window, $, templates) ->

  bindables = '*[data-bind]'
  bindings = {}
  bindingIds = 0


  safeEval = (expression, context) ->
    body = "with(context) { return #{expression}; }"
    fn = new Function 'context', body
    fn context


  class binder

    constructor: (element, elementAttribute, provider, expression) ->
      @element = element
      @elementAttribute = elementAttribute
      @provider = provider
      @expression = expression
      @provider.onchange @updateDom

    updateDom: (provider) =>
      value = safeEval @expression, window.state

      if @elementAttribute == 'text'
        @element.text value
      else if @elementAttribute == 'html'
        @element.html value
      else if @elementAttribute == 'style'
        @element.css value
      else
        @element.attr @elementAttribute, value 


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

    # split `text: provider_name.nested.attr` on `:` into it's components
    components = target.split /:(.+)/

    # target attribute of element that needs updating when data changes,
    # e.g. text, html, id, data-something
    elementAttribute = components[0].trim()

    # the right portion of the binding, everything after `:`
    expression = components[1].trim()

    # extract the provider name from an expression using the trapper mechanism
    providerName = catchProvider expression
    provider = window.state.get providerName
    instance = new binder(element, elementAttribute, provider, expression)
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

