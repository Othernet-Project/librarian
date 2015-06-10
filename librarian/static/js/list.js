(function (window, $) {
  var win = $(window);
  var doc = $(document);
  var body = $('html,body');
  var contentList = $('#content-list');
  var totalPages = parseInt(contentList.data('total'), 10);
  var footer = $('.footer');
  var winHeight;
  var loader = $(templates.loading);
  var end = $(templates.end);
  var toTop = $(templates.toTop);
  var loadLink = $(templates.loadLink);
  var loading = false;

  var contentPath = window.location.pathname;
  var contentQuery = new URI(window.location.search);
  var params = contentQuery.search(true);
  var page = parseInt(params.p, 10);

  var showToTop = _.debounce(toggleToTopButton, 50);

  // Normalize pager vales
  if (page == null || isNaN(page) || Array.isArray(page)) { page = 1; }
  if (isNaN(totalPages)) { totalPages = 1; }

  // Content loading
  if (totalPages > 1) {
    contentList.after(loadLink);
    loadLink.on('click', loadContent);
  }

  // Preload the spinner and other elements
  contentList.after(loader);
  loader.hide();
  contentList.after(end);
  end.hide();
  contentList.after(toTop);
  toTop.hide();

  // Go-to-top animation
  $('.to-top').click(animateTopScroll);

  // Fix height data
  updateHeight();

  // Inifinite scrolling
  $('.pager-links').remove();  // No pager needed
  $('.paging').remove();
  win.on('scroll', showToTop);
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
      loadLink.hide();
      loadContent = function () {};
      loading = false;
      return;
    }

    
    // Formulate params for the new page
    params.p = page = page + 1;
    contentQuery.search(params);
    url = contentPath + contentQuery.search();

    // Fetch the HTML data
    loadLink.hide();
    loader.show();
    xhr = $.get(url);
    xhr.done(insertContent);
    xhr.fail(insertFailure);
  }

  function insertContent(res) {
    res = $.trim(res);
    if (res === '') { return loadEmpty(); }
    res = $(res);
    contentList.append(res);
    loader.hide();
    loadLink.show();
    win.trigger('listUpdate', [res]);
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

  function toggleToTopButton() {
    if (win.scrollTop() > winHeight) {
      toTop.fadeIn(200);
    } else {
      toTop.fadeOut(200);
    }
  }

  function animateTopScroll(e) {
    e.preventDefault();
    body.animate({'scrollTop': 0}, 500);
  }

}(this, jQuery));
