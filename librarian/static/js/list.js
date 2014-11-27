!function (window, $) {
  var win = $(window);
  var doc = $(document);
  var contentList = $('#content-list');
  var totalPages = parseInt(contentList.data('total'), 10);
  var footer = $('.footer');
  var winHeight;
  var masonry;
  var loader = $(templates.loading);
  var end = $(templates.end);
  var loading = false;

  var contentPath = window.location.pathname;
  var contentQuery = new URI(window.location.search);
  var params = contentQuery.search(true);
  var page = parseInt(params.p, 10);

  var onScroll = _.debounce(loadContent, 50);

  // Normalize pager vales
  if (page == null || isNaN(page) || Array.isArray(page)) { page = 1; }
  if (isNaN(totalPages)) { totalPages = 1; }

  // Preload the spinner
  contentList.after(loader);
  loader.hide();
  contentList.after(end);
  end.hide();

  // Tiled column layout
  contentList.masonry({
    itemSelector: '.data',
    isAnimatedFromBottom: true
  });

  // Fix layout once more after images are loaded
  contentList.imagesLoaded(function () { contentList.masonry(); });

  // Fix height data
  updateHeight();

  // Inifinite scrolling
  $('.pager-links').remove();  // No pager needed
  $('.paging').remove();
  win.on('scroll', onScroll);
  win.on('resize', updateHeight);

  // Utility functions and callbacks

  function updateHeight(e) {
    winHeight = win.height();
  }

  function loadContent(e) {
    var docPos;
    var docHeight;
    var url;
    var xhr;

    if (loading) { return; }
    loading = true;

    docPos = win.scrollTop();
    docHeight = doc.height() - winHeight * 2;

    if (docPos < docHeight) { 
      loading = false;
      return; 
    }

    if (page + 1 > totalPages) {
      end.show();
      loadContent = function () {};
      loading = false;
      return;
    }

    
    // Formulate params for the new page
    params.p = page = page + 1;
    contentQuery.search(params);
    url = contentPath + contentQuery.search();

    // Fetch the HTML data
    loader.show();
    xhr = $.get(url);
    xhr.done(insertContent);
    xhr.fail(insertFailure);
  }

  function insertContent(res) {
    res = $.trim(res);
    if (res === '') { return loadEmpty(); }
    loader.hide();
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
