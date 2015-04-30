/*jslint browser: true*/
(function ($, Pikaday) {
    'use strict';
    $('#noscript-picker').hide();
    $('#datepicker').css('display', 'inline-block');

    function zeroPad(str, count) {
        str = str.toString();
        return str.length < count ? zeroPad("0" + str, count) : str;
    }

    var dateStr = '{0}-{1}-{2}'.replace('{0}', $('#year').val())
                               .replace('{1}', zeroPad($('#month').val(), 2))
                               .replace('{2}', zeroPad($('#day').val(), 2)),
        picker = new Pikaday({
            field: document.getElementById('datepicker'),
            container: document.getElementById('pikaday-container'),
            onSelect: function (date) {
                $('input[name="year"]').val(date.getFullYear());
                $('select[name="month"]').val(date.getMonth() + 1);
                $('input[name="day"]').val(date.getDate());
            },
            onClose: function () {
                picker.setDate(picker.toString());
            }
        });

    picker.setDate(dateStr);
}(this.jQuery, this.Pikaday));
