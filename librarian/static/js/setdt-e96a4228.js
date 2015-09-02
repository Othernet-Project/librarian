/*jslint browser: true*/
(function ($) {
    'use strict';
    var self = {};

    self.timezoneSelected = function () {
        // when second select is chosen, populate the hidden select field
        // which will actually be posted
        self.timezone.val($(this).val());
    };

    self.timezoneRegionSelected = function () {
        // when region selector is changed, create secondary select for exact location
        var selectedOpt = $(this),
            first = selectedOpt.val(),
            timezoneSelector;

        $('#second-level').remove();
        timezoneSelector = $('<select />').attr('id', 'second-level').append(function () {
            var options = [];
            // populate new select element by filtering on the region selector's
            // value and creating new option elements from the data
            $.each(self.tzOptions, function (i, opt) {
                if (opt.value.substring(0, first.length) === first) {
                    var tzText = opt.value.replace(first + '/', '')
                                          .replace('_', ' ')
                                          .replace('\u005F', ' '),
                        newOpt = $('<option />').val(opt.value).text(tzText);

                    options.push(newOpt);
                }
            });
            // set first option from the new listas the currently selected value
            self.timezone.val(options[0].val());
            return options;
        }).on('change', self.timezoneSelected);

        self.timezoneContainer.append(timezoneSelector);
    };

    self.initTimezoneSelector = function () {
        var firstLevel = [],
            regionSelector;

        self.timezone.hide();
        // collect region strings only
        $.each(self.tzOptions, function (i, option) {
            var first = option.value.split('/')[0];

            if ($.inArray(first, firstLevel) === -1) {
                firstLevel.push(first);
            }
        });
        // create region selector element from previously collected data
        regionSelector = $('<select />').append(function () {
            return $.map(firstLevel, function (value) {
                return $('<option />').val(value).text(value);
            });
        }).on('change', self.timezoneRegionSelected);

        self.timezoneContainer.append(regionSelector);

        self.timezoneRegionSelected.call(regionSelector);
    };

    $('.js-error').show();
    self.timezoneContainer = $('.timezone-container');
    self.timezone = $('#id_timezone');
    self.tzOptions = self.timezone.find('option');
    self.initTimezoneSelector();
}(this.jQuery));
