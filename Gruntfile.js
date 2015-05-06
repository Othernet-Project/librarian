/*global require,module*/
var crypto = require('crypto');

module.exports = function (grunt) {
    'use strict';
    var staticRoot = 'librarian/static/',
        cssSrc = 'assets/scss',
        cssDest = staticRoot + 'css/',
        jsSrc = 'assets/js/',
        jsDest = staticRoot + 'js/',
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
            return jsSrc + filename;
        });
    }

    // prefix each filename in `jsBundles` with `jsSrc`
    Object.keys(jsBundles).forEach(function (key) {
        jsBundles[key] = prefixJS.apply(this, jsBundles[key]);
    });

    // construct uglify configuration
    uglifyConfig = Object.keys(jsBundles).reduce(function (confs, key) {
        var config = {
                options: {
                    sourceMap: true,
                    sourceMapName: jsDest + key + '.js.map'
                },
                files: {}
            };
        config.files[jsDest + key + '.js'] = jsBundles[key];
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
        clean: {
            build: {
                src: staticRoot + 'dist'
            }
        },
        compass: {
            dist: {
                options: {
                    httpPath: '/static/',
                    basePath: staticRoot,
                    cssDir: 'css',
                    sassDir: '../../' + cssSrc,
                    imagesDir: 'img',
                    javascriptsDir: 'js',
                    relativeAssets: false,
                    outputStyle: 'compressed'
                }
            }
        },
        hash: {
            options: {
                mapping: staticRoot + 'assets.json',
                srcBasePath: staticRoot,
                destBasePath: staticRoot + 'dist/',
                flatten: false,
                hashLength: 8,
                hashFunction: function (source, encoding) {
                    return crypto.createHash('sha1').update(source, encoding).digest('hex');
                }
            },
            js: {
                src: jsDest + '*.js',
                dest: staticRoot + 'dist/js/'
            },
            css: {
                src: cssDest + '*.css',
                dest: staticRoot + 'dist/css/'
            }
        },
        uglify: uglifyConfig
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-hash');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('build', ['compass', 'uglify', 'clean', 'hash']);
};
