//#-------------------------------------------------- BEGIN [gulp file for SGP Project] - (25-10-2017 - 16:51:17) {{
var gulp = require('gulp');
var gulpBrowser = require("gulp-browser");
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');

var jsxFilesDir = './static/jsx/*.js';
var jsOutPutDir = './static/js/chat';

// tasks
gulp.task('del', function () {
  return del([jsOutPutDir]);
});

gulp.task('default', ['del'], function () {
  gulp.start('transform');
  gulp.watch(jsxFilesDir, ['transform']);
});

gulp.task('transform', function () {
  var stream = gulp.src(jsxFilesDir)
    .pipe(gulpBrowser.browserify({transform: ['reactify']}))
    .pipe(gulp.dest(jsOutPutDir))
    .pipe(size());
  return stream;
});
//#-------------------------------------------------- END   [gulp file for SGP Project] - (25-10-2017 - 16:51:17) }}
