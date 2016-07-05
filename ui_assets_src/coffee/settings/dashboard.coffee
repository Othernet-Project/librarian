((window, $, templates) ->

  section = $ '#dashboard-settings'
  form = null
  url = null
  errorMessage = templates.settingsSaveError
  successMessage = templates.settingsSaveOK
  win = $ window


  removeMessage = () ->
    (form.find '.o-form-message').slideUp () ->
      ($ this).remove()


  submitData = (data) ->
    res = $.post url, data
    res.done (data) ->
      form.html data
      form.prepend successMessage
      (form.parents '.o-collapsible-section').trigger 'remax'
      win.trigger 'settings-saved'
      setTimeout removeMessage, 5000
    res.fail () ->
      form.prepend errorMessage


  initPlugin = (e) ->
    form = section.find '#settings-form'
    url = form.attr 'action'
    form.on 'submit', (e) ->
      e.preventDefault()
      data = form.serialize()
      submitData data

  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates
