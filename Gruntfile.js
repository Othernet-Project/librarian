/*global require,module*/
var crypto = require('crypto');

module.exports = function (grunt) {
    'use strict';
    var staticRoot = 'librarian/static/',
        cssSrc = 'assets/scss/',
        cssDest = staticRoot + 'css/',
        imgSrc = 'assets/img/',
        imgDest = staticRoot + 'img/',
        jsSrc = 'assets/js/',
        jsDest = staticRoot + 'js/',
        jsBundles = {
            content: ['tags.js', 'list.js'],
            dashboard: ['collapsible_dash_sections.js'],
            reader: ['jquery.js', 'lodash.js', 'templates.js', 'tags.js', 'patcher.js'],
            ui: ['jquery.js', 'lodash.js', 'templates.js', 'URI.js'],
            setupdatetime: ['setdt.js']
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
                    sourceMapIncludeSources: true
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
                    cssSrc + '**/*.scss',
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
            hashed: {
                src: staticRoot + 'dist'
            },
            source: {
                src: [cssDest, jsDest, staticRoot + 'dist/js/*.map']
            }
        },
        compass: {
            dist: {
                options: {
                    httpPath: '/static/',
                    basePath: staticRoot,
                    cssDir: 'css',
                    sassDir: '../../' + cssSrc,
                    imagesDir: '../../' + imgSrc,
                    generatedImagesDir: 'img',
                    httpGeneratedImagesPath: '/static/img/',
                    javascriptsDir: 'js',
                    relativeAssets: false,
                    outputStyle: 'compressed'
                }
            }
        },
        copy: {
            src: {
                files: [{
                    expand: true,
                    flatten: true,
                    src: [jsSrc + '*.js'],
                    dest: jsDest,
                    filter: 'isFile'
                }]
            },
            dist: {
                files: [{
                    expand: true,
                    flatten: true,
                    src: [jsDest + '*.map'],
                    dest: staticRoot + 'dist/js/',
                    filter: 'isFile'
                }, {
                    expand: true,
                    flatten: true,
                    src: [imgSrc + '*'],
                    dest: imgDest,
                    filter: 'isFile'
                }]
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
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-hash');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('build', ['compass', 'uglify', 'clean:hashed', 'copy:src', 'hash', 'copy:dist']);
    grunt.registerTask('dist', ['build', 'clean:source']);
};
