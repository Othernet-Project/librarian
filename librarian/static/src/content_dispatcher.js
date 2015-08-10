/*jslint browser: true*/
(function ($) {
    'use strict';
    var contentType = $('.reader').data('content-type');
    $.contentReaders[contentType]();
}(this.jQuery));
