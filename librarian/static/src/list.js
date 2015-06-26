/*jslint browser: true*/
/*jslint indent: 2*/
/*jslint nomen: true*/
/*jslint vars: true*/
(function (window, $, _, URI) {
  'use strict';
  var win = $(window);
  var doc = $(document);
  var body = $('html,body');
  var contentList = $('#content-list');
  var totalPages = parseInt(contentList.data('total'), 10);
  var winHeight;
  var loader = $(window.templates.loading);
  var end = $(window.templates.end);
  var toTop = $(window.templates.toTop);
  var loadLink = $(window.templates.loadLink);
  var loading = false;

  var contentPath = window.location.pathname;
  var contentQuery = new URI(window.location.search);
  var params = contentQuery.search(true);
  var page = parseInt(params.p, 10);

  var showToTop;

  // Utility functions and callbacks

  function updateHeight() {
    winHeight = win.height();
  }

  function loadEmpty() {
    // TODO: implement loading empty
    console.log('Empty');
  }

  function insertContent(res) {
    res = $.trim(res);
    if (res === '') { return loadEmpty(); }
    res = $(res);
    contentList.append(res);
    loadLink.removeClass('active');
    loadLink.text(loadLink.data('normal'));
    win.trigger('listUpdate', [res]);
    loading = false;
  }

  function insertFailure() {
    // TODO: implement failure handling
    console.log('Not implemented');
  }

  function loadContent() {
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

    // Formulate params for the new page
    params.p = page = page + 1;
    contentQuery.search(params);
    url = contentPath + contentQuery.search();

    // Fetch the HTML data
    loadLink.addClass('active');
    loadLink.text(loadLink.data('active'));
    xhr = $.get(url);
    xhr.done(insertContent);
    xhr.fail(insertFailure);

    if (page + 1 > totalPages) {
      end.show();
      loadLink.hide();
      loadContent = function () {};
      loading = false;
      return;
    }
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

  showToTop = _.debounce(toggleToTopButton, 50);

  // Normalize pager vales
  if (page === null || isNaN(page) || Array.isArray(page)) { page = 1; }
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
  $('.pager').remove();  // No pager needed
  win.on('scroll', showToTop);
  win.on('resize', updateHeight);
}(this, this.jQuery, this._, this.URI));
