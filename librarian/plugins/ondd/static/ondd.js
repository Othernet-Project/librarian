/*jslint indent: 2 */
(function (window, $) {
  var signalStatus = $('#signal-status');
  var url = signalStatus.data('url');
  var fileList = $('#ondd-file-list');
  var filesUrl = fileList.data('url');

  var refreshDelay = 3000;  // ms
  var refreshInterval = 3000;  // ms
  var fileRefreshInterval = 30000;  // ms
  var satSelection = $(window.templates.satPresets);
  var satSelector = satSelection.find('select');
  var settingsForm;
  var fields;
  var submitButton;
  var defaultData = {
    frequency: '',
    symbolrate: '',
    delivery: '1',
    modulation: 'qp',
    polarization: '0'
  };

  doRefresh(refreshInterval);
  doRefreshFileList(fileRefreshInterval);
  initForm();

  function initForm() {
    settingsForm = $('#settings-form');
    fields = settingsForm.find('.settings-fields');
    submitButton = settingsForm.find('button');
    fields.before(satSelection);
    satSelector.on('change', updateForm);
    updateForm();
    submitButton.on('click', submitForm);
  }

  function submitForm(event) {
    event.preventDefault();
    $.post(settingsForm.attr('action'), settingsForm.serialize(), function (result) {
      submitButton.off();
      satSelector.off();
      settingsForm.replaceWith(result);
      initForm();
    });
  }

  function doRefresh(interval) {
    setTimeout(function () {
      $.get(url).done(function (result) {
        signalStatus.html(result);
      }).always(function () {
        doRefresh(interval);
      });
    }, interval);
  }

  function doRefreshFileList(interval) {
    if (fileList.length > 0) {
      setTimeout(function () {
        $.get(filesUrl).done(function (result) {
          fileList.html(result);
        }).always(function () {
          doRefreshFileList(interval);
        });
      }, interval);
    }
  }

  function updateForm(e) {
    var valId = satSelector.val();
    fillFormFromSelection(valId);
    submitButton.toggle(valId !== '0');
    if (valId === '-1') {
      fields.slideDown();
    } else {
      fields.slideUp();
    }
  }

  function getOptionData(valId) {
    selection = satSelector.find('option[value=' + valId + ']');
    if (!selection.length) {
      return defaultData;
    }
    return selection.data();
  }

  function fillFormFromSelection(valId) {
    var data;
    var selection;

    if (valId === '0' || valId === '-1') {
      data = defaultData;
    } else {
      data = getOptionData(valId)
    }
    fillForm(data);
  }

  function fillForm(obj) {
    var key;
    for (key in obj) {
      settingsForm.find('#' + key).val(obj[key]);
    }
  }
}(this, this.jQuery));
