/* Legacy PLAYER bridge. Preview: native hardware execution is not validated. */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) { module.exports = factory(); }
    else { root.HubLegacyPlayer = factory(); }
}(this, function () {
    'use strict';
    var api = {}, sequence = 0;
    function seconds(value) { value = Number(value); return isFinite(value) ? Math.max(0, value) : 0; }
    api.create = function (plugin, notify) {
        var state = {currentTime: 0, duration: 0, paused: true, ended: false, error: null};
        var opened = false, started = false, closed = false, url = '', offset = 0, names = [], id = ++sequence;
        var required = ['Play', 'ResumePlay', 'Stop', 'Pause', 'Resume', 'JumpForward', 'JumpBackward', 'GetDuration', 'SetDisplayArea'];
        required.forEach(function (name) {
            if (!plugin || typeof plugin[name] === 'undefined') { throw new Error('TV player API is unavailable.'); }
        });
        function snapshot() {
            return {currentTime: state.currentTime, duration: state.duration, paused: state.paused, ended: state.ended, error: state.error, engine: 'Samsung Legacy PLAYER'};
        }
        function emit(type) { if (!closed && opened) { notify(type, snapshot()); } }
        function checked(result) { if (result === false || result === 0) { throw new Error('TV player rejected the operation.'); } }
        function fail(code) {
            if (closed || !opened || state.error) { return; }
            state.error = code; state.paused = true;
            try { plugin.Stop(); } catch (ignored) {}
            emit('error');
        }
        function callback(property, fn) {
            var name = 'event' + id + '_' + property;
            api[name] = function (value) { if (!closed && opened && !state.error) { fn(value); } };
            plugin[property] = 'HubLegacyPlayer.' + name;
            names.push({property: property, name: name});
        }
        callback('OnStreamInfoReady', function () {
            try { state.duration = seconds(plugin.GetDuration()) / 1000; emit('loadedmetadata'); }
            catch (ignored) { fail('metadata'); }
        });
        callback('OnCurrentPlayTime', function (value) {
            if (state.ended || value === null || !isFinite(Number(value)) || Number(value) < 0) { return; }
            state.currentTime = seconds(value) / 1000;
            emit(state.paused ? 'pause' : 'playing'); emit('timeupdate');
        });
        callback('OnBufferingStart', function () { emit('waiting'); });
        callback('OnBufferingComplete', function () { if (!state.paused) { emit('playing'); } });
        callback('OnRenderingComplete', function () {
            if (state.ended) { return; }
            state.ended = true; state.paused = true;
            if (state.duration > 0) { state.currentTime = state.duration; }
            emit('timeupdate'); emit('ended');
        });
        ['OnConnectionFailed', 'OnAuthenticationFailed', 'OnNetworkDisconnected', 'OnRenderError', 'OnStreamNotFound'].forEach(function (name) {
            callback(name, function () { fail(name); });
        });
        return {
            snapshot: snapshot,
            load: function (source, resume) {
                if (closed) { throw new Error('TV player is closed.'); }
                if (!/^(https?:\/\/|file:\/\/\/)/i.test(source) || /[\u0000-\u0020<>"\\]/.test(source)) {
                    throw new Error('Unsupported TV playback URL.');
                }
                if (/^https?:\/\//i.test(source)) {
                    var authority = source.replace(/^https?:\/\//i, '').split(/[/?#]/)[0];
                    if (!authority || authority.indexOf('@') !== -1) { throw new Error('Unsupported TV playback URL.'); }
                }
                if (opened) { opened = false; try { plugin.Stop(); } catch (ignored) {} }
                url = source; offset = seconds(resume); started = false;
                state = {currentTime: offset, duration: 0, paused: true, ended: false, error: null};
                opened = true;
            },
            play: function () {
                if (closed || !opened || state.error) { return; }
                try {
                    if (!started || state.ended) {
                        if (state.ended) { offset = 0; state.currentTime = 0; state.ended = false; }
                        checked(plugin.SetDisplayArea(0, 0, 960, 540));
                        state.paused = false; emit('waiting');
                        if (offset > 0) { checked(plugin.ResumePlay(url, Math.floor(offset))); }
                        else { checked(plugin.Play(url)); }
                        started = !state.error;
                    } else if (state.paused) {
                        checked(plugin.Resume()); state.paused = false; emit('playing');
                    }
                } catch (ignored) { fail('start'); }
            },
            pause: function () {
                if (closed || !started || state.paused || state.ended || state.error) { return; }
                try { checked(plugin.Pause()); state.paused = true; emit('pause'); }
                catch (ignored) { fail('pause'); }
            },
            seek: function (amount) {
                if (closed || !started || !state.duration || state.ended || state.error) { return; }
                var target = Math.max(0, Math.min(state.duration, state.currentTime + Number(amount)));
                var difference = target - state.currentTime, distance = Math.floor(Math.abs(difference));
                if (!isFinite(distance) || distance < 1) { return; }
                try {
                    emit('waiting');
                    checked(difference > 0 ? plugin.JumpForward(distance) : plugin.JumpBackward(distance));
                } catch (ignored) { fail('seek'); }
            },
            close: function () {
                if (closed) { return; }
                closed = true; opened = false;
                try { plugin.Stop(); } catch (ignored) {}
                names.forEach(function (entry) {
                    if (plugin[entry.property] === 'HubLegacyPlayer.' + entry.name) { plugin[entry.property] = ''; }
                    // Leave a no-op target for callbacks already queued by the native engine.
                    api[entry.name] = function () {};
                });
            }
        };
    };
    return api;
}));
