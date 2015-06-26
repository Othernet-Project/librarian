/**
 * dropdown.js: dropdown menu event handling
 *
 * Copyright 2015, Outernet Inc.
 * Some rights reserved.
 *
 * This software is free software licensed under the terms of GPLv3. See
 * COPYING file that comes with the source code, or
 * http://www.gnu.org/licenses/gpl.txt.
 */

(function (window, $) {
    'use strict';
    $('.dropdown-toggle').each(function () {
        var dropdown = $(this).parent('.dropdown'),
            dropdownBody = dropdown.find('.dropdown-body');

        function toggleDropdown(event) {
            dropdownBody.toggle();
            event.stopPropagation();
        }

        dropdown.on('click', toggleDropdown);
    });
    $('body').click(function (event) {
        $('.dropdown-body').hide();
    });
}(this, this.jQuery));
