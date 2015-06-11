(function (window, $) {
  var menu = $('#nav');
  var hamburger = $('.hamburger');

  hamburger.on('click', toggleMenu);

  function switchMenu(e) {
    if (isDesktop()) {
      desktopMenu();
    } else {
      mobileMenu();
    }
  }

  function mobileMenu() {

  }

  function desktopMenu() {

  }

  function isDesktop() {
    return hamburger.style('display') == 'none';
  }

  function toggleMenu(e) {
    e.preventDefault();
    menu.toggleClass('open');
  }

}(this, this.jQuery));
