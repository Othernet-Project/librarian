/*jslint browser: true*/
(function ($) {
    'use strict';
    $.contentReaders = $.contentReaders || {};
    $.contentReaders.image = function () {
        var imageURLs = JSON.parse($('#imageURLs').html()).urls,
            imgEl = $('.image-container img'),
            prevButton = $('.previous'),
            nextButton = $('.next');

        function loadImage(imgIndex) {
            if (imgIndex >= 0 && imgIndex < imageURLs.length) {
                imgEl.data('index', imgIndex);
                imgEl.fadeOut(function () {
                    imgEl.attr('src', imageURLs[imgIndex]).fadeIn();
                });

                if (imgIndex === 0) {
                    prevButton.css('visibility', 'hidden');
                } else {
                    prevButton.css('visibility', 'visible');
                }

                if (imgIndex === imageURLs.length - 1) {
                    nextButton.css('visibility', 'hidden');
                } else {
                    nextButton.css('visibility', 'visible');
                }
            }
        }

        function prevImage(e) {
            loadImage(parseInt(imgEl.data('index'), 10) - 1);
            e.preventDefault();
        }

        function nextImage(e) {
            loadImage(parseInt(imgEl.data('index'), 10) + 1);
            e.preventDefault();
        }

        prevButton.click(prevImage);
        nextButton.click(nextImage);
    };
}(this.jQuery));
