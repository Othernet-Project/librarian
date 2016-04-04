((window, $, templates) ->

  onddForm = $ '#ondd-form'

  # Ignore if not the currect step
  if not onddForm.length
    return

  msg = onddForm.find '.o-form-message'
  if msg.length
    setTimeout () ->
      msg.slideUp 500
    , 5000

  transponders = onddForm.find '#transponders'
  testButton = onddForm.find '#tuner-test'

  onTransponderSwitch = () ->
    val = transponders.val()
    testButton.attr 'disabled', val is '0'

  transponders.on 'change', onTransponderSwitch
  onTransponderSwitch()

) this, this.jQuery, this.templates
