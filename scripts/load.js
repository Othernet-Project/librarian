/*globals phantom*/
(function () {
    'use strict';
    var self = {},
        page = require('webpage').create(),
        system = require('system');

    if (system.args.length < 3) {
        console.log("Usage: load.js <taskId> <url> [<silent>]");
        phantom.exit();
    }

    self.log = function (status, taskId, url, timeTaken) {
        console.log("----> {0}[{1}] {2} in {3}ms".replace("{0}", status.toUpperCase())
                                                 .replace("{1}", taskId)
                                                 .replace("{2}", url)
                                                 .replace("{3}", timeTaken));
    };

    self.run = function (taskId, url, silent) {
        var startTime = Date.now();

        page.open(url, function (status) {
            var timeTaken = Date.now() - startTime;

            if (!silent) {
                self.log(status, taskId, url, timeTaken);
            }
            console.log(JSON.stringify({
                success: status === 'success',
                time: timeTaken
            }));
            phantom.exit();
        });
    };

    self.run(system.args[1], system.args[2], system.args[3]);
}());
