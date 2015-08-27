(function (window, $) {
    'use strict';
    var self = {},
        signalStatus = $('#signal-status'),
        url = signalStatus.data('url'),
        fileList = $('#ondd-file-list'),
        filesUrl = fileList.data('url'),

        refreshInterval = 3000,  // ms
        fileRefreshInterval = 30000,  // ms
        satSelection = $(window.templates.satPresets),
        satSelector = satSelection.find('select'),
        settingsForm,
        fields,
        submitButton,
        defaultData = {
            frequency: '',
            symbolrate: '',
            delivery: '1',
            modulation: 'qp',
            polarization: '0'
        };

    self.equalObjects = function (a, b, soft) {
        var key,
            valsMismatch;

        for (key in a) {
            if (a.hasOwnProperty(key)) {
                valsMismatch = soft ? a[key] != b[key] : a[key] !== b[key];
                if (!b.hasOwnProperty(key) || valsMismatch) {
                    return false;
                }
            }
        }
        for (key in b) {
            if (b.hasOwnProperty(key) && !a.hasOwnProperty(key)) {
                return false;
            }
        }
        return true;
    };

    self.getOptionData = function (valId) {
        var selection = satSelector.find('option[value=' + valId + ']');
        if (!selection.length) {
            return defaultData;
        }
        return selection.data();
    };

    self.fillForm = function (obj) {
        var key;
        for (key in obj) {
            if (obj.hasOwnProperty(key)) {
                settingsForm.find('#id_' + key).val(obj[key]);
            }
        }
    };

    self.fillFormFromSelection = function (valId) {
        var data;

        if (valId === '0') {
            data = defaultData;
        } else if (valId === '-1') {
            data = self.getCurrentData();
        } else {
            data = self.getOptionData(valId);
        }
        self.fillForm(data);
    };

    self.updateForm = function () {
        var valId = satSelector.val();

        self.fillFormFromSelection(valId);
        submitButton.toggle(valId !== '0');
        if (valId === '-1') {
            fields.slideDown();
        } else if (fields.is(':visible')) {
            fields.slideUp();
        }
    };

    self.submitForm = function (event) {
        event.preventDefault();
        $.post(settingsForm.attr('action'), settingsForm.serialize(), function (result) {
            var oldDisplay = fields.css('display');
            submitButton.off();
            satSelector.off();
            settingsForm.replaceWith(result);
            self.initForm();
            fields.css('display', oldDisplay);
            settingsForm.find('.message').delay(5000).fadeOut();
        });
    };

    self.getCurrentData = function () {
        var currentData = {};

        fields.find('input').each(function () {
            var el = $(this),
                value = el.attr('value');

            if (value !== undefined) {
                currentData[el.attr('name')] = value;
            }
        });

        fields.find('select').each(function () {
            var select = $(this),
                selectedOption = select.find('option[selected="None"]'),
                value = selectedOption.val();

            if (value !== undefined) {
                currentData[select.attr('name')] = value;
            }
        });

        return currentData;
    };

    self.selectSavedPreset = function () {
        var currentData = self.getCurrentData(),
            options = satSelector.find('option'),
            isEqual = false,
            opt,
            i;

        for (i = 0; i < options.length; i += 1) {
            opt = $(options[i]);
            isEqual = self.equalObjects(opt.data(), currentData, true);
            if (isEqual) {
                satSelector.val(opt.val());
                break;
            }
        }

        if (!isEqual && !self.equalObjects(currentData, {})) {
            // custom parameters
            satSelector.val(-1);
        }
    };

    self.initForm = function () {
        settingsForm = $('#settings-form');
        fields = settingsForm.find('.settings-fields');
        fields.before(satSelection);
        submitButton = settingsForm.find('button');
        submitButton.on('click', self.submitForm);
        satSelector.on('change', self.updateForm);
        self.selectSavedPreset();
        self.updateForm();
    };

    self.doRefresh = function (interval) {
        setTimeout(function () {
            $.get(url).done(function (result) {
                signalStatus.html(result);
            }).always(function () {
                self.doRefresh(interval);
            });
        }, interval);
    };

    self.doRefreshFileList = function (interval) {
        if (fileList.length > 0) {
            setTimeout(function () {
                $.get(filesUrl).done(function (result) {
                    fileList.html(result);
                }).always(function () {
                    self.doRefreshFileList(interval);
                });
            }, interval);
        }
    };

    self.doRefresh(refreshInterval);
    self.doRefreshFileList(fileRefreshInterval);
    self.initForm();
}(this, this.jQuery));
