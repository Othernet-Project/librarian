/*jslint browser: true*/
(function ($) {
    'use strict';
    $.contentReaders = $.contentReaders || {};
    $.contentReaders.video = function () {
        $('video').mediaelementplayer();
    };
}(this.jQuery));
