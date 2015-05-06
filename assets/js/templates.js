;(function (window, $) {
  window.templates = (function() {
    var templates = {};
    $('script[type="text/template"]').each(function () {
      var el = $(this);
      var name = el.attr('id');
      templates[name] = $.trim(el.html());
    });
    return templates;
  }());
}(this, jQuery));
