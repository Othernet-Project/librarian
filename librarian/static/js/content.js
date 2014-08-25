!function (window, $) {
  $('#go-button').remove();
  $('#page').change(forceSubmit);
  $('#perpage').change(forceSubmit);
  function forceSubmit(e) {
    $('#pager').submit();
  }
}(this, jQuery);
