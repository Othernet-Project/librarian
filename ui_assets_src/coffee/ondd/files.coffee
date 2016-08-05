((window, $) ->

  section = $ '#dashboard-ondd'


  initPlugin = (e) ->
    return


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery
