((window, $, templates) ->

  bindables = '*[data-bind]'
  bindings = {}
  bindingIds = 0


  class binder

    constructor: (element, elementAttribute, provider, dataPath) ->
      @element = element
      @elementAttribute = elementAttribute
      @provider = provider
      @dataPath = dataPath
      @provider.onchange (@updateDom.bind @)

    updateDom: (provider) ->
      data = provider.get()

      if @dataPath.length > 0
        extractor = (src, key) -> src[key]
        value = @dataPath.reduce extractor, data
      else
        value = data

      if @elementAttribute == 'text'
        @element.text value
      else if @elementAttribute == 'html'
        @element.html value
      else
        @element.attr @elementAttribute, value 


  bindTo = (element, bindingId) ->
    target = element.data 'bind'
    # split `text: data_source.nested.attr` on `:` into it's components
    components = target.split /:(.+)/
    # target attribute of element that needs updating when data changes
    elementAttribute = components[0].trim()
    # split `provider_name.nested.attr` on `.` into it's segments
    segments = components[1].trim().split '.'
    providerName = segments[0]
    dataPath = segments.slice 1
    provider = window.state.get providerName
    instance = new binder(element, elementAttribute, provider, dataPath)
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

