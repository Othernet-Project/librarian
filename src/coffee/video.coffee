((window, $, templates) ->
  'use strict'

  videoPlayer = Object.create mediaPlayer
  videoPlayer.super = mediaPlayer
  videoPlayer.initialize = (container) ->
    @super.initialize.call(@, container)

  videoPlayer.readyPlayer = ->
    controls = @container.find('#video-controls-video').first()
    controls.mediaelementplayer {
      features: ['playpause', 'progress', 'duration', 'volume', 'fullscreen'],
      success: (mediaElement) =>
        @onPlayerReady(mediaElement)
        return
    }
    return

  videoPlayer.updatePlayer = (item) ->
    @super.updatePlayer.call(@, item)
    @player.play()
    return

  prepareVideo = () ->
    controls = $ '#video-controls'
    if not controls.length
      return
    videoPlayer.initialize $('#main-container')
    return

  prepareVideo()
  window.onTabChange prepareVideo

  return
) this, this.jQuery, this.templates
