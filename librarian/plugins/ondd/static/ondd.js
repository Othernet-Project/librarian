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
                settingsForm.find('#' + key).val(obj[key]);
            }
        }
    };

    self.fillFormFromSelection = function (valId) {
        var data;

        if (valId === '0' || valId === '-1') {
            data = defaultData;
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
        } else {
            fields.slideUp();
        }
    };

    self.submitForm = function (event) {
        event.preventDefault();
        $.post(settingsForm.attr('action'), settingsForm.serialize(), function (result) {
            submitButton.off();
            satSelector.off();
            settingsForm.replaceWith(result);
            self.initForm();
        });
    };

    self.initForm = function () {
        settingsForm = $('#settings-form');
        fields = settingsForm.find('.settings-fields');
        submitButton = settingsForm.find('button');
        fields.before(satSelection);
        satSelector.on('change', self.updateForm);
        self.updateForm();
        submitButton.on('click', self.submitForm);
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
