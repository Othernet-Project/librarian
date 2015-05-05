/*global require,module*/
module.exports = function (grunt) {
    'use strict';
    var staticRoot = 'librarian/static/',
        jsRoot = staticRoot + 'js/',
        jsBundles = {
            content: ['tags.js', 'list.js'],
            dashboard: ['collapsible_dash_sections.js'],
            reader: ['jquery.js', 'lodash.js', 'templates.js', 'tags.js'],
            ui: ['jquery.js', 'lodash.js', 'templates.js', 'URI.js'],
            setupdatetime: ['pikaday.js', 'setdt.js']
        },
        uglifyConfig;

    function prefixJS() {
        var args = Array.prototype.slice.call(arguments);
        return args.map(function (filename) {
            return jsRoot + filename;
        });
    }

    // prefix each filename in `jsBundles` with `jsRoot`
    Object.keys(jsBundles).forEach(function (key) {
        jsBundles[key] = prefixJS.apply(this, jsBundles[key]);
    });

    // construct uglify configuration
    uglifyConfig = Object.keys(jsBundles).reduce(function (confs, key) {
        var config = {
                options: {
                    sourceMap: true,
                    sourceMapName: jsRoot + key + '.js.map'
                },
                files: {}
            };
        config.files[jsRoot + key + '.js'] = jsBundles[key];
        confs[key] = config;
        return confs;
    }, {});

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            scss: {
                files: [
                    'scss/**/*.scss',
                ],
                tasks: ['compass']
            },
            jsContent: {
                files: jsBundles.content,
                tasks: ['uglify:content']
            },
            jsDashboard: {
                files: jsBundles.dashboard,
                tasks: ['uglify:dashboard']
            },
            jsReader: {
                files: jsBundles.reader,
                tasks: ['uglify:reader']
            },
            jsUi: {
                files: jsBundles.ui,
                tasks: ['uglify:ui']
            },
            jsSetupdatetime: {
                files: jsBundles.setupdatetime,
                tasks: ['uglify:setupdatetime']
            }
        },
        compass: {
            dist: {
                options: {
                    httpPath: '/static/',
                    basePath: staticRoot,
                    cssDir: 'css',
                    sassDir: '../../scss',
                    imagesDir: 'img',
                    javascriptsDir: 'js',
                    relativeAssets: false,
                    outputStyle: 'compressed'
                }
            }
        },
        uglify: uglifyConfig
    });

    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('build', ['compass', 'uglify']);
};
