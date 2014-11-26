!function (window, $) {
  var win = $(window);
  var doc = $(document);
  var contentList = $('#content-list');
  var footer = $('.footer');
  var winHeight;
  var loadOffset;   
  var masonry;
  var loading = false;

  var contentPath = window.location.pathname;
  var contentQuery = new URI(window.location.search);
  var params = contentQuery.search(true);
  var page = parseInt(params.p, 10);

  if (page == null || isNaN(page) || Array.isArray(page)) { page = 1; }

  updateHeight();

  // Tiled column layout
  contentList.masonry({
    itemSelector: '.data',
    isAnimatedFromBottom: true
  });

  contentList.imagesLoaded(function () { contentList.masonry(); });

  // Inifinite scrolling
  $('.pager-links').remove();  // No pager needed
  $('.paging').remove();
  win.on('scroll', loadContent);
  win.on('resize', updateHeight);

  // Utility functions and callbacks

  function updateHeight(e) {
    winHeight = win.height();
    loadOffset = winHeight * 0.4; // 40% of window height
  }

  function loadContent(e) {
    var docPos = win.scrollTop() + winHeight;
    var docHeight = doc.height() - loadOffset;
    var url;
    var xhr;

    if (loading) { return; }

    if (docPos < docHeight) { return; }
    
    // Formulate params for the new page
    params.p = page = page + 1;
    contentQuery.search(params);
    url = contentPath + contentQuery.search();

    // Fetch the HTML data
    loading = true;
    xhr = $.get(url);
    xhr.done(insertContent);
    xhr.fail(insertFailure);
  }

  function insertContent(res) {
    res = $.trim(res);
    if (res === '') { return loadEmpty(); }
    res = $(res);
    contentList.append(res).imagesLoaded(function () {
      contentList.masonry('appended', res);
    });
    loading = false;
  }

  function insertFailure() {
    // TODO: implement failure handling
    console.log('Not implemented');
  }

  function loadEmpty() {
    // TODO: implement loading empty
    console.log('Empty');
  }
}(this, jQuery);
