!function(window, $) {
  var checkboxes = $('.downloads-selection input[type=checkbox]');
  $('.sel-all').on('click', function (e) {
    e.preventDefault();
    checkboxes.prop('checked', true);
    checkboxes.change();
  });
  $('.sel-none').on('click', function (e) {
    e.preventDefault();
    checkboxes.prop('checked', false);
    checkboxes.change();
  });
  checkboxes.on('change', function (e) { toggleCheckboxRow($(this)); });
  checkboxes.each(function(idx, el) { toggleCheckboxRow($(el)); });

  function toggleCheckboxRow(checkbox) {
    checkbox.parents('tr').toggleClass('selected', checkbox.prop('checked'));
  }
}(this, jQuery);
