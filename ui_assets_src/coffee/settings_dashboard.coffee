((window, $, templates) ->

  form = $ '#settings-form'
  url = form.attr 'action'
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


  form.on 'submit', (e) ->
    e.preventDefault()
    data = form.serialize()
    submitData data

) this, this.jQuery, this.templates
