((window, $) ->
  'use strict'

  $.extend mejs.MepDefaults, {
    nextText: 'Next', #templates.nextTrackText,
    prevText: 'Previous', #templates.previousTrackText,
  }

  $.extend MediaElementPlayer.prototype, {
    buildnext: (player, controls, layers, media) ->
      nextButtonTemplate = '<div class="mejs-button mejs-next-button mejs-next">' +
        '<button type="button" aria-controls="' + player.id + '" title="' + player.options.nextText + '"></button>' +
        '</div>'

      nextButtonHandler = (e) ->
        $(media).trigger 'mep-ext-playnext'
        return
      nextButton = $(nextButtonTemplate)
        .appendTo(controls)
        .click(nextButtonHandler)
      return

    buildprev: (player, controls, layers, media) ->
      prevButtonTemplate = '<div class="mejs-button mejs-prev-button mejs-prev">' +
        '<button type="button" aria-controls="' + player.id + '" title="' + player.options.prevText + '"></button>' +
        '</div>'

      prevButtonHandler = (e) ->
        $(media).trigger 'mep-ext-playprev'
        return
      prevButton = $(prevButtonTemplate)
        .appendTo(controls)
        .click(prevButtonHandler)
      return
  }

  return

) this, this.mejs.$
