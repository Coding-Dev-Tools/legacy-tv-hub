'use strict';
var fs = require('fs'), path = require('path'), acorn = require('acorn');
['core.js', 'app.js'].forEach(function (name) {
    acorn.parse(fs.readFileSync(path.join(__dirname, 'app', name), 'utf8'), {ecmaVersion: 5});
});
['platform.js', 'player.js'].forEach(function (name) {
    acorn.parse(fs.readFileSync(path.join(__dirname, 'adapters', 'samsung-legacy', name), 'utf8'), {ecmaVersion: 5});
});
acorn.parse(fs.readFileSync(path.join(__dirname, 'adapters', 'browser-cache', 'offline.js'), 'utf8'), {ecmaVersion: 5});
console.log('PASS: every application script parses as ECMAScript 5.');
