((window, $, templates) ->

  defaultSuccess = templates.modalContent
  defaultFailure = templates.modalLoadFailure
  body = $ document.body
  win = $ window
  ESCAPE = 27

  $.fn.closeModal = () ->
    elem = $ this
    if elem.hasClass 'o-modal-overlay'
      modal = elem
    else
      modal = elem.parents '.o-modal-overlay'
    if not modal.length
      return
    modal.remove()
    win.trigger 'modalclose'
    return

  body.on 'click', '.o-modal-overlay', (e) ->
    ($ this).closeModal()

  body.on 'click', '.o-modal-close', (e) ->
    ($ this).closeModal()

  body.on 'click', '.o-modal-window', (e) ->
    e.stopPropagation()

  body.on 'keydown', '.o-modal-window', (e) ->
    if e.which == ESCAPE
      ($ this).closeModal()


  $.modalDialog = (template) ->
    # Kill old modal
    ($ '.o-modal-overlay').closeModal()
    modal = $ template
    modal.appendTo body
    win.trigger 'modalcreate'
    modal


  $.modalContent = (contentUrl, options) ->
    options ?= {}
    options.successTemplate ?= defaultSuccess
    options.failureTemplate ?= defaultFailure
    options.fullScreen ?= false
    {successTemplate, failureTemplate, fullScreen} = options

    # Make a new modal
    modal = $.modalDialog successTemplate
    window = modal.find '.o-modal-window'
    panel = modal.find '.o-modal-panel'

    if fullScreen
      window.addClass 'o-full-screen'

    # Add the modal window to body and focus it
    window.focus()

    # Load the contents
    res = $.get contentUrl
    res.done (data) ->
      panel.html data
      win.trigger 'modalload'
    res.fail () ->
      panel.html failureTemplate
      win.trigger 'modalloaderror'

    res

) this, this.jQuery, this.templates
