'use strict';
var assert = require('assert'), fs = require('fs'), vm = require('vm');
var script = fs.readFileSync('adapters/browser-cache/offline.js', 'utf8');
var version = require('./package.json').version;
function fixture(hash) {
    var events = {}, requests = [], cache = {status: 1, swapCache: function () {}, addEventListener: function (name, fn) { events[name] = fn; }};
    var sandbox = {window: {HubVersion: version, location: {hash: hash}, applicationCache: cache, addEventListener: function () {}}, document: {querySelector: function () { return null; }}};
    sandbox.XMLHttpRequest = function () {
        this.open = function (method, path) { requests.push({method: method, path: path}); };
        this.setRequestHeader = function () {};
        this.send = function (body) { requests[requests.length - 1].body = JSON.parse(body); this.readyState = 4; this.status = 204; this.onreadystatechange(); };
    };
    vm.runInNewContext(script, sandbox);
    return {events: events, requests: requests, location: sandbox.window.location};
}
var normal = fixture(''); normal.events.cached(); normal.events.noupdate();
assert.strictEqual(normal.requests.length, 0, 'Regular offline use sends no reports');
var token = 'a'.repeat(32), setup = fixture('#setup=' + token);
setup.events.downloading(); setup.events.updateready(); setup.events.error();
assert.strictEqual(setup.requests.length, 0, 'An incomplete save/update must not acknowledge readiness');
setup.events.cached(); setup.events.noupdate();
assert.strictEqual(setup.requests.length, 1);
assert.deepStrictEqual(setup.requests[0], {method: 'POST', path: '/_setup/ready?run=' + token, body: {version: version}});
assert.strictEqual(setup.location.hash, '', 'The temporary setup fragment is removed after acknowledgment');
var invalid = fixture('#setup=invalid'); invalid.events.cached();
assert.strictEqual(invalid.requests.length, 0);
console.log('PASS: offline setup acknowledges a completed cache once; ordinary use sends no reports.');
