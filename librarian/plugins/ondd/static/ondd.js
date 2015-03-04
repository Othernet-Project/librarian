(function (window, $) {
  var signalStatus = $('#signal-status');
  var url = signalStatus.data('url');
  var fileList = $('#ondd-file-list');
  var filesUrl = fileList.data('url');

  var refreshDelay = 3000;  // ms
  var refreshInterval = 3000;  // ms
  var satSelection = $(window.templates.satPresets);
  var satSelector = satSelection.find('select');
  var settingsForm = $('#settings-form');
  var fields = settingsForm.find('.settings-fields');
  var submitButton = settingsForm.find('button');
  var defaultData = {
    frequency: '',
    symbolrate: '',
    delivery: '1',
    modulation: 'qp',
    polarization: '0'
  };

  fields.before(satSelection);
  $(function() {
    setInterval(doRefresh, refreshInterval);
  })

  satSelector.on('change', updateForm);
  updateForm();

  function doRefresh() {
    signalStatus.load(url);
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
      return defaultData();
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
