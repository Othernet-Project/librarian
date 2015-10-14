(function (window, $) {

  $(".deselect").click(function() {
    $('input[type=checkbox]').prop('checked', false);
  });
  $(".select").click(function() {
    $('input[type=checkbox]').prop('checked', true);
  });

  $(".check").click(function() {
    var md5_list = [];
    var serial_form = $('form').serializeArray();
    for (var i = 0; i < serial_form.length; i++) {
      var md5 = serial_form[i].value;
      console.log(md5);
      md5_list.push(md5);
    }
    var page = $('.pager').data('page');
    var base_string = location.href.replace(location.search,"");
    var new_href = base_string + '?p=' + page + '&check=' + md5_list.join(separator=',');
    location.href = new_href;
  });

}(this, jQuery));
