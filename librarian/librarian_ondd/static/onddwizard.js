(function (window, $) {
    'use strict';
    var self = {},
        nextButton = $('.setup-wizard button'),
        settingsForm = $('#settings-form'),
        satPresetSelect = settingsForm.find('select[name="preset"]'),
        errTemplate = $(window.templates.jsFieldError),
        messages = JSON.parse($('#validation-messages').html());

    self.validatePresetSelect = function (event) {
        var selectedPreset = satPresetSelect.val(),
            errEl = $(errTemplate).text(messages.preset);

        if (selectedPreset === '0') {
            satPresetSelect.after(errEl);
            event.preventDefault();
        }
    };

    self.clearValidationMessages = function () {
        settingsForm.find('.field-error.js-error').remove();
    };

    satPresetSelect.on('change', self.clearValidationMessages);
    nextButton.click(self.validatePresetSelect);
}(this, this.jQuery));
