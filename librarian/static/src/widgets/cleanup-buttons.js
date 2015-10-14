(function (window, $) {
  $(document).ready(function () {
    $('input[type=checkbox]').prop('checked', false);
  });

  $(".deselect").click(function() {
    $('input[type=checkbox]').prop('checked', false);
  });
  $(".select").click(function() {
    $('input[type=checkbox]').prop('checked', true);
  });

  $(".check").click(function() {
    var md5_list = [];
    $('input[type=checkbox]').each(function () {
      var md5 = (this.checked ? $(this).attr('value') : "");
      if (md5 === "") {
        return;
      }
      md5_list.push(md5);
    });
    var page = $('.pager').data('page');
    var base_string = location.href.replace(location.search,"");
    var new_href = base_string + '?p=' + page + '&check=' + md5_list.join(separator=',');
    location.href = new_href;
  });

}(this, jQuery));
