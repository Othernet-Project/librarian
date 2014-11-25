!function (window, $) {
  $('#go-button').remove();
  $('#page').change(forceSubmit);
  $('#perpage').change(forceSubmit);
  function forceSubmit(e) {
    $('#pager').submit();
  }

  new Masonry($('#content-list')[0], {
    itemSelector: '.data'
  });
}(this, jQuery);
