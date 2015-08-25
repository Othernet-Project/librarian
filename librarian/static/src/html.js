/*jslint browser: true*/
(function ($) {
    'use strict';
    $.contentReaders = $.contentReaders || {};
    $.contentReaders.html = function () {
        var head,
            readerFrame = $(document).find('#reader-main'),
            keepFormatting = readerFrame.data('keep-formatting'),
            readerCssPatch = $(window.templates.readerCssPatch);

        function applyStylePatch() {
            var readerDoc = readerFrame.contents();
            if (!keepFormatting) {
                head = readerDoc.find('head');
                if (head.length === 0) {
                    head = $('<head></head>');
                    readerDoc.append(head);
                }
                head.append(readerCssPatch);
            }
        }

        readerFrame.load(applyStylePatch);
        if (readerFrame.contents().prop('readyState') === 'complete') {
            applyStylePatch();
        }
    };
}(this.jQuery));
