(function (window, $) {

  $(".deselect").click(function() {
    $('input[type=checkbox]').prop('checked', false);
  });
  $(".select").click(function() {
    $('input[type=checkbox]').prop('checked', true);
  });

}(this, jQuery));
