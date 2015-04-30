(function ($) {
    'use strict';
    var self = {},
        nextButton = $('.setup-wizard button'),
        satPresetSelect = $('#settings-form select[name="preset"]'),
        errMsg = $('#preset-error-msg').val();

    self.validatePresetSelect = function (event) {
        var selectedPreset = satPresetSelect.val(),
            errEl = $('<span class="field-error js-error" id="preset-error">{0}</span>'.replace('{0}', errMsg));

        if (selectedPreset === '0') {
            satPresetSelect.after(errEl);
            event.preventDefault();
        }
    };

    self.clearValidationMessages = function () {
        $('.field-error.js-error').remove();
    };

    satPresetSelect.on('change', self.clearValidationMessages);
    nextButton.click(self.validatePresetSelect);
}(this.jQuery));
