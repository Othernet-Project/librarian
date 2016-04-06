((window, $, templates) ->
  'use strict'

  playNext = (e) ->
    player = e.data
    next = ($ '.playlist-list-item-current').next '.playlist-list-item'
    if next.length
      musicPlayer.playlist.next()
      musicPlayer.player.play()
    return

  musicPlayer = Object.create mediaPlayer
  musicPlayer.super = mediaPlayer
  musicPlayer.initialize = (container) ->
    features = {
      toggleSidebarOnSelect: false
    }
    @audioData = JSON.parse($("#audioData").html())
    @super.initialize.call(@, container, features)
    return

  musicPlayer.readyPlayer = ->
    controls = @container.find('#audio-controls-audio').first()
    controls.mediaelementplayer {
      features: ['playpause', 'progress', 'duration', 'volume'],
      success: (mediaElement) =>
        mediaElement.play()
        @onPlayerReady mediaElement
        return
    }
    return

  musicPlayer.updatePlayer = (item, autoPlay) ->
    @super.updatePlayer.call(@, item, autoPlay)
    @updateCover item.data('get-thumb-url'), @audioData.defaultThumbUrl
    return

  musicPlayer.updateCover = (url, defaultUrl) ->
    options = @options
    res = $.get url
    res.done (data) ->
      cover = $ options.coverSelector
      if data.url
        cover.attr 'src', data.url
        cover.addClass options.customCoverClass
      else
        cover.attr 'src', defaultUrl
        cover.removeClass options.customCoverClass
      return
    return

  prepareAudio = () ->
    controls = $ '#audio-controls'
    if not controls.length
      return
    musicPlayer.initialize $("#main-container")
    ($ musicPlayer.player).on 'ended', musicPlayer, playNext
    ($ '#audio-controls-albumart').on 'click', (e) ->
      e.preventDefault()
      if musicPlayer.player.paused
        musicPlayer.player.play()
      else
        musicPlayer.player.pause()
      return
    ($ window).on 'playlist-updated', () ->
      trackInfo = ($ '.playlist-list-item-current').data()
      title = trackInfo.title
      artist = trackInfo.author or trackInfo.artist or template.unknownAuthor
      ($ '#audio-controls-title h2').text title
      ($ '#audio-controls-title p').text artist
    return

  $ prepareAudio
  window.onTabChange prepareAudio

  return
) this, this.jQuery, this.templates
