(function (window, $) {
  var body = $('body');
  var hamburger = $('.hamburger');
  var menu = $(window.templates.menu);
  var lvl2triggers = menu.find('.level2-trigger');
  var lvl1triggers = menu.find('.top-trigger');
  var lvl2containers = menu.find('.level2');

  body.append(menu);

  hamburger.on('click', toggleMenu);
  lvl2triggers.on('click', toggleLvl2);
  lvl1triggers.on('click', closeLevel2);

  function toggleMenu(e) {
    e.preventDefault();
    closeLevel2();
    menu.toggleClass('open');
    hamburger.toggleClass('open');
  }

  function toggleLvl2(e) {
    var tgt = $(this);
    e.preventDefault();
    closeLevel2();
    $(tgt.attr('href')).addClass('open');
  }

  function closeLevel2() {
    lvl2containers.removeClass('open');
  }
}(this, this.jQuery));
