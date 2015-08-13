/*jslint browser: true*/
(function ($) {
    'use strict';
    $(document).ready(function () {
        var contentType = $('.reader').data('content-type'),
            handler = $.contentReaders[contentType];

        if (handler) {
            handler();
        }
    });
}(this.jQuery));
