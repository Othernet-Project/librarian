/*jslint browser: true*/
(function ($) {
    'use strict';
    var metaButton = $('.reader-meta .toggle'),
        metaContainer = metaButton.parent(),
        reader = $('.reader-frame');

    metaButton.on('click', function () {
        metaContainer.toggleClass('expanded');
        reader.toggleClass('reduced');
    });
}(this.jQuery));
