/*jslint browser: true*/
(function ($) {
    'use strict';
    $(document).ready(function () {
        var contentType = $('.reader').data('content-type');
        $.contentReaders[contentType]();
    });
}(this.jQuery));
