'use strict';
var assert = require('assert'), bridge = require('./adapters/samsung-legacy/player');
var fs = require('fs'), vm = require('vm');
function fixture() {
    var calls = [], events = [], plugin = {}, methods = ['Play', 'ResumePlay', 'Stop', 'Pause', 'Resume', 'JumpForward', 'JumpBackward', 'SetDisplayArea'];
    methods.forEach(function (method) { plugin[method] = function () { calls.push([method].concat(Array.prototype.slice.call(arguments))); return true; }; });
    plugin.GetDuration = function () { return 10000; };
    var player = bridge.create(plugin, function (type, state) { events.push({type: type, state: state}); });
    function emit(property, value) { var name = plugin[property].split('.')[1]; bridge[name](value); }
    function opened() { player.load('https://example.com/video.mp4', 0); player.play(); }
    return {calls: calls, events: events, plugin: plugin, player: player, emit: emit, opened: opened};
}
assert.throws(function () { bridge.create({}, function () {}); }, /unavailable/);
var f = fixture();
['javascript:alert(1)', 'data:video/mp4,test', 'https://', 'https://user:password@example.com/a.mp4', 'https://example.com/a b.mp4'].forEach(function (url) {
    assert.throws(function () { f.player.load(url, 0); }, /Unsupported/);
});
assert.strictEqual(f.calls.length, 0);
f.opened();
assert.deepStrictEqual(f.calls.slice(0, 2), [['SetDisplayArea', 0, 0, 960, 540], ['Play', 'https://example.com/video.mp4']]);
assert.strictEqual(f.events.some(function (e) { return e.type === 'playing'; }), false);
f.emit('OnStreamInfoReady'); f.emit('OnCurrentPlayTime', 2500);
assert.strictEqual(f.player.snapshot().duration, 10);
assert.strictEqual(f.player.snapshot().currentTime, 2.5);
f.player.pause(); f.emit('OnCurrentPlayTime', 2700);
assert.strictEqual(f.player.snapshot().paused, true, 'Queued time callback must not undo Pause');
f.player.play(); assert.strictEqual(f.calls[f.calls.length - 1][0], 'Resume');
f.emit('OnCurrentPlayTime', NaN);
assert.strictEqual(f.player.snapshot().currentTime, 2.7, 'Malformed time must not erase the saved position');
f = fixture(); f.player.load('https://example.com/video.mp4', 42.9); f.player.play();
assert.deepStrictEqual(f.calls[1], ['ResumePlay', 'https://example.com/video.mp4', 42]);
f = fixture(); f.opened(); f.emit('OnStreamInfoReady'); f.emit('OnCurrentPlayTime', 4000);
f.player.seek(100); assert.deepStrictEqual(f.calls[f.calls.length - 1], ['JumpForward', 6]);
assert.strictEqual(f.player.snapshot().currentTime, 4, 'Seeking waits for a native time report');
f.player.seek(-100); assert.deepStrictEqual(f.calls[f.calls.length - 1], ['JumpBackward', 4]);
var count = f.calls.length; f.player.seek(NaN); assert.strictEqual(f.calls.length, count);
f = fixture(); f.opened(); f.emit('OnAuthenticationFailed');
assert.strictEqual(f.player.snapshot().error, 'OnAuthenticationFailed');
assert.strictEqual(f.calls[f.calls.length - 1][0], 'Stop');
count = f.calls.length; f.player.play(); assert.strictEqual(f.calls.length, count);
f.player.load('https://example.com/another.mp4', 0); assert.strictEqual(f.player.snapshot().error, null);
f = fixture(); f.plugin.Play = function () { return false; }; f.opened();
assert.strictEqual(f.player.snapshot().error, 'start');
f = fixture(); f.plugin.Play = function () { f.emit('OnAuthenticationFailed'); return true; }; f.opened();
assert.strictEqual(f.events[f.events.length - 1].type, 'error', 'A synchronous failure must remain visible');
f = fixture(); f.opened(); f.emit('OnStreamInfoReady'); f.player.pause();
f.plugin.JumpForward = function () { f.emit('OnCurrentPlayTime', 6000); return true; };
f.player.seek(6);
assert.strictEqual(f.player.snapshot().currentTime, 6);
assert.strictEqual(f.player.snapshot().paused, true);
assert.strictEqual(f.events[f.events.length - 2].type, 'pause', 'Seeking a paused video must preserve its visible pause state');
f = fixture(); f.opened(); f.emit('OnStreamInfoReady'); f.emit('OnRenderingComplete');
assert.strictEqual(f.player.snapshot().ended, true); assert.strictEqual(f.player.snapshot().currentTime, 10);
f.player.play(); assert.strictEqual(f.player.snapshot().ended, false); assert.strictEqual(f.player.snapshot().currentTime, 0);
f = fixture(); f.opened();
var queuedCallback = bridge[f.plugin.OnCurrentPlayTime.split('.')[1]];
f.player.close(); count = f.events.length; queuedCallback(9000); f.player.close();
assert.strictEqual(f.events.length, count); assert.strictEqual(f.plugin.OnCurrentPlayTime, '');
var infoCalls = [], infoPlugin = {
    Open: function () { infoCalls.push(['Open'].concat(Array.prototype.slice.call(arguments))); return true; },
    Execute: function (name) { infoCalls.push([name]); return name === 'GetFirmware' ? 'T-TESTFAMILY-1000.0' : 'test-system'; }
};
var sandbox = {Common: {API: {Widget: function () {}, TVKeyValue: function () {}}}, document: {getElementById: function () { return infoPlugin; }}};
vm.runInNewContext(fs.readFileSync('adapters/samsung-legacy/platform.js', 'utf8'), sandbox);
assert.strictEqual(sandbox.HubPlatform.runtimeInfo().firmware, 'T-TESTFAMILY-1000.0');
assert.deepStrictEqual(infoCalls.map(function (row) { return row[0]; }), ['Open', 'GetFirmware', 'GetSystemVersion']);
infoPlugin.Execute = function () { throw new Error('Unavailable'); };
assert.strictEqual(sandbox.HubPlatform.runtimeInfo().firmware, 'Unavailable');
console.log('PASS: native bridge contract: timing, pause/resume, bounded seeking, rejected operations, recovery, cleanup and read-only firmware access. Hardware execution remains unverified.');
