((window, $, templates) ->

  bindables = '*[data-bind]'
  bindings = {}
  bindingIds = 0


  class binder

    constructor: (element, elementAttribute, provider, expression) ->
      @element = element
      @elementAttribute = elementAttribute
      @provider = provider
      @expression = expression
      @provider.onchange (@updateDom.bind @)

    updateDom: (provider) ->
      body = "with(state) { return #{@expression}; }"
      fn = new Function 'state', body
      value = fn window.state

      if @elementAttribute == 'text'
        @element.text value
      else if @elementAttribute == 'html'
        @element.html value
      else
        @element.attr @elementAttribute, value 


  bindTo = (element, bindingId) ->
    target = element.data 'bind'

    # split `text: provider_name.nested.attr` on `:` into it's components
    components = target.split /:(.+)/

    # target attribute of element that needs updating when data changes,
    # e.g. text, html, id, data-something
    elementAttribute = components[0].trim()

    # the right portion of the binding, everything after `:`
    expression = components[1].trim()

    # extract the provider name from an expression like `provider.nested.attr`
    match = expression.match /[a-zA-Z_$][a-zA-Z_$0-9]*/
    if match.length != 1
      throw new Error "Invalid binding: " + target

    # get provider name from match
    providerName = match[0]
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

