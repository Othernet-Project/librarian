/*jslint browser: true*/
/*globals Pikaday,$*/
(function () {
    'use strict';
    document.getElementById('noscript-picker').style.display = 'none';
    document.getElementById('datepicker').style.display = 'inline-block';

    var picker = new Pikaday({
        field: document.getElementById('datepicker'),
        container: document.getElementById('pikaday-container'),
        onSelect: function (date) {
            $('input[name="year"]').val(date.getFullYear());
            $('select[name="month"]').val(date.getMonth() + 1);
            $('input[name="day"]').val(date.getDate());
        }
    });
}());
