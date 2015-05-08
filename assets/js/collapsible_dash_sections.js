!function (window, $) {
  var dashHeaders = $('.dash-section h2');
  var dashCollapsibles = $('.dash-collapsible');

  _.each(dashHeaders, addIcon);
  dashHeaders.on('click', expandCollapse);

  function expandCollapse(e) {
    e.preventDefault();
    $(e.target).parents('.dash-collapsible').toggleClass('dash-collapsed');
  }

  function addIcon(hdr) {
    $(hdr).prepend(templates.collapseIcon);
  }
}(this, jQuery);
