/**
 * progress.js: progress widget utility functions
 *
 * Copyright 2015, Outernet Inc.
 * Some rights reserved.
 * 
 * This software is free software licensed under the terms of GPLv3. See
 * COPYING file that comes with the source code, or
 * http://www.gnu.org/licenses/gpl.txt.
 */

(function (window, $) {
  $.fn.progress = function() {
    var el = $(this);
    var label = el.find('.label');
    var value = el.find('.value');
    var bar = el.find('.bar');
    var threshold = parseInt(el.data('threshold'));

    if (isNaN(threshold)) {
      threshold = 0;
    }

    return {
      updateValues: function(p, v) {
        if (!v) { v = p + '%'; }
        value.text(v);
        bar.width(p + '%');
        el.toggleClass('low', p < threshold);
      },

      updateLabel: function(s) {
        label.text(s); 
      }
    };
  };
}(this, this.jQuery));
