/**
 * accordion.js: accordion widget event handling
 *
 * Copyright 2015, Outernet Inc.
 * Some rights reserved.
 * 
 * This software is free software licensed under the terms of GPLv3. See
 * COPYING file that comes with the source code, or
 * http://www.gnu.org/licenses/gpl.txt.
 */

(function (window, $) {

  $.fn.accordion = function() {
    var el = $(this);
    var sectionHeaders = el.find('.accordion-section > :first-child');
    
    el.addClass('active');
    
    // Add section icons
    sectionHeaders.each(function() {
      var header = $(this);
      var section = header.parent('.accordion-section');
      var headerLink = $('<a>');
      var headerIcon = $('<span>');

      headerLink.attr('href', 'javascript:void(0)');
      headerIcon.addClass('accordion-icon');
      headerLink.text(header.text());
      header.html(headerIcon);
      header.append(headerLink);
    });

    sectionHeaders.on('click', toggleSection);

    function toggleSection(e) {
      var section = $(this).parent('.accordion-section');
      if (section.hasClass('non-collapsible')) {
        return;
      }
      section.toggleClass('expanded');
    }
  }

}(this, this.jQuery));
