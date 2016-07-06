((window, $, templates) ->

  section = $ '#dashboard-ondd'
  onddForm = null
  url = null
  errorMessage = templates.onddSettingsError


  submitData = (data) ->
    res = $.post url, data
    res.done (data) ->
      onddForm.html data
      ($ window).trigger 'transponder-updated'
    res.fail () ->
      onddForm.prepend errorMessage


  initPlugin = (e) ->
    onddForm = $ '#ondd-form'
    url = onddForm.attr 'action'
    onddForm.on 'submit', (e) ->
      e.preventDefault()
      data = onddForm.serialize()
      submitData data


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates
