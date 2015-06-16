/*jslint browser: true*/
(function ($) {
    'use strict';
    var head,
        readerDoc,
        readerFrame = $(document).find('#reader-main'),
        keepFormatting = readerFrame.data('keep-formatting'),
        readerCssPatch = $(window.templates.readerCssPatch);

    readerFrame.load(function () {
        readerDoc = readerFrame.contents();
        if (!keepFormatting) {
            head = readerDoc.find('head');
            if (head.length === 0) {
                head = readerDoc.append('<head></head>');
            }
            head.append(readerCssPatch);
        }
    });
}(this.jQuery));
