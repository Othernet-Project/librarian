/*jslint browser: true*/
(function ($, MediaElementPlayer) {
    'use strict';
    $.contentReaders = $.contentReaders || {};
    $.contentReaders.audio = function () {
        var player = new MediaElementPlayer('#audio-player');

        function playTrack() {
            var track = $(this).parent(),
                url = track.data('url'),
                title = track.find('.title').text();

            $('#audio-title').text(title);
            player.pause();
            player.setSrc(url);
            player.play();
        }

        $('.play').on('click', playTrack);
    };
}(this.jQuery, this.MediaElementPlayer));
