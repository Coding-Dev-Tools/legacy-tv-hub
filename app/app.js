(function () {
    'use strict';
    var core = window.HubCore, content, video, store, data, persistent, platform = null, nativeKeys = null;
    var view = 'home', active = null, resume = 0, lastSave = 0, editingField = 'url', caps = false;
    var keys = {UP: 38, DOWN: 40, LEFT: 37, RIGHT: 39, ENTER: 13, RETURN: 8, EXIT: 27, PLAY: 415, PAUSE: 19, STOP: 413, FF: 417, REW: 412};
    function element(tag, className, text) {
        var node = document.createElement(tag);
        if (className) { node.className = className; }
        if (typeof text !== 'undefined') { node.textContent = text; }
        return node;
    }
    function put(parent, tag, className, text) { var node = element(tag, className, text); parent.appendChild(node); return node; }
    function button(parent, text, action, className) {
        var node = put(parent, 'button', className || '', text);
        node.type = 'button'; node.onclick = action; return node;
    }
    function notice(text) { document.getElementById('notice').textContent = text; }
    function persist() { persistent = core.save(store, data); if (!persistent) { notice('Changes are kept for this session only.'); } }
    function begin(name, title, lead) {
        view = name; content.innerHTML = ''; content.className = ''; content.scrollTop = 0;
        if (title) { put(content, 'p', 'eyebrow', 'Your TV, a little more useful'); put(content, 'h1', '', title); }
        if (lead) { put(content, 'p', 'lead', lead); }
    }
    function focusFirst() { var nodes = focusable(); if (nodes.length) { nodes[0].focus(); } }
    function focusable() {
        var all = document.querySelectorAll('button,input'), output = [], i;
        for (i = 0; i < all.length; i += 1) {
            if (!all[i].disabled && all[i].offsetWidth && all[i].offsetHeight) { output.push(all[i]); }
        }
        return output;
    }
    function move(direction) {
        var current = document.activeElement, nodes = focusable(), box, x, y, best = null, score = Infinity, i, other, dx, dy, candidate;
        if (!current || current === document.body) { focusFirst(); return; }
        box = current.getBoundingClientRect(); x = box.left + box.width / 2; y = box.top + box.height / 2;
        for (i = 0; i < nodes.length; i += 1) {
            if (nodes[i] === current) { continue; }
            other = nodes[i].getBoundingClientRect(); dx = other.left + other.width / 2 - x; dy = other.top + other.height / 2 - y;
            if ((direction === 'LEFT' && dx >= -2) || (direction === 'RIGHT' && dx <= 2) || (direction === 'UP' && dy >= -2) || (direction === 'DOWN' && dy <= 2)) { continue; }
            candidate = direction === 'LEFT' || direction === 'RIGHT' ? Math.abs(dx) + 3 * Math.abs(dy) : Math.abs(dy) + 3 * Math.abs(dx);
            if (candidate < score) { score = candidate; best = nodes[i]; }
        }
        if (best) { best.focus(); }
        else if (direction === 'DOWN' || direction === 'UP') { content.scrollTop += direction === 'DOWN' ? 180 : -180; }
    }
    function card(parent, number, title, description, action, accent) {
        var node = button(parent, '', action, 'card' + (accent ? ' accent' : ''));
        put(node, 'span', 'number', number); put(node, 'strong', '', title); put(node, 'small', '', description); return node;
    }
    function recent() {
        return data.items.slice(0).sort(function (a, b) { return b.played - a.played; }).filter(function (item) { return item.played > 0; });
    }
    function home() {
        begin('home', 'Make room for your videos.', 'A simple home for direct video links, favorites and where you left off.');
        var cards = put(content, 'div', 'cards'), items = recent();
        card(cards, '01 / WATCH', 'Play a video', 'Add a direct video link using your remote.', function () { editor(); }, true);
        card(cards, '02 / COLLECTION', 'My videos', data.items.length + ' saved ' + (data.items.length === 1 ? 'video' : 'videos') + ' on this TV.', function () { library(false); });
        card(cards, '03 / PICK UP', 'Continue watching', items.length ? items[0].title : 'Your recently played videos will appear here.', function () { library(true); });
        card(cards, '04 / TRY IT', 'Play the demo', 'A bundled 10-second video. No internet needed.', demo);
        card(cards, '05 / COMFORT', 'Display & help', 'Contrast, playback support and app information.', about);
        focusFirst();
    }
    function library(onlyRecent) {
        begin('library', onlyRecent ? 'Continue watching' : 'My videos', 'Direct video links saved on this device.');
        var toolbar = put(content, 'div', 'toolbar'), items = onlyRecent ? recent() : data.items.slice(0);
        button(toolbar, 'Add a video', function () { editor(); }); button(toolbar, 'Home', home);
        if (!items.length) { put(content, 'p', 'empty', 'Nothing here yet. Add a direct video link, or try the bundled demo from Home.'); }
        items.forEach(function (item) {
            var row = put(content, 'div', 'video-row'), copy = put(row, 'div', 'video-copy'), actions = put(row, 'div', 'video-actions');
            put(copy, 'h2', '', item.title);
            put(copy, 'p', '', core.resumeAt(item) ? 'Continue at ' + core.time(item.position) : 'Ready to play');
            button(actions, core.resumeAt(item) ? 'Resume' : 'Play', function () { start(item, false); });
            button(actions, 'Edit', function () { editor(item); });
            button(actions, 'Remove', function () { confirmRemove(item); });
        });
        focusFirst();
    }
    function confirmRemove(item) {
        begin('confirm'); var box = put(content, 'div', 'confirm');
        put(box, 'h1', '', 'Remove this saved video?'); put(box, 'p', 'muted', item.title + ' will be removed from this app. The original video is unchanged.');
        button(box, 'Keep video', function () { library(false); });
        button(box, 'Remove from library', function () {
            data.items = data.items.filter(function (row) { return row !== item; }); persist(); library(false); notice('Saved video removed.');
        }); focusFirst();
    }
    function editor(item) {
        begin('editor'); content.className = 'editor';
        put(content, 'h1', '', item ? 'Edit video' : 'Add a video');
        var titleRow = put(content, 'div', ''), urlRow = put(content, 'div', ''), title, url;
        var label = put(titleRow, 'label', 'field-label', 'Name'); label.htmlFor = 'title-input';
        title = put(titleRow, 'input', ''); title.id = 'title-input'; title.maxLength = 90; title.value = item ? item.title : ''; title.onfocus = function () { editingField = 'title'; };
        label = put(urlRow, 'label', 'field-label', 'Link'); label.htmlFor = 'url-input';
        url = put(urlRow, 'input', ''); url.id = 'url-input'; url.maxLength = 4096; url.value = item ? item.url : 'https://'; url.onfocus = function () { editingField = 'url'; };
        put(content, 'p', 'muted editor-hint', 'Use a direct MP4 or a stream your TV supports. A service’s watch-page address will not work.');
        var keyboard = put(content, 'div', 'keyboard'), rows = ['qwertyuiop12', 'asdfghjkl345', 'zxcvbnm67890', ':/.?=&_-#%+[]'];
        rows.forEach(function (characters) {
            var row = put(keyboard, 'div', 'key-row');
            characters.split('').forEach(function (character) { button(row, character, function () { append(caps ? character.toUpperCase() : character); }); });
        });
        var controls = put(content, 'div', 'keyboard-controls');
        function target() { return editingField === 'title' ? title : url; }
        function append(text) { var field = target(); field.value = (field.value + text).slice(0, field.maxLength); }
        button(controls, 'Name / Link', function () { editingField = editingField === 'url' ? 'title' : 'url'; notice('Keyboard is editing: ' + (editingField === 'url' ? 'Link' : 'Name')); });
        button(controls, 'a / A', function () { caps = !caps; notice(caps ? 'Uppercase letters' : 'Lowercase letters'); });
        button(controls, 'Space', function () { append(' '); });
        button(controls, 'Backspace', function () { target().value = target().value.slice(0, -1); });
        button(controls, 'Clear', function () { target().value = ''; });
        button(controls, 'http://', function () { target().value = 'http://'; });
        var error = put(content, 'p', 'error'); error.id = 'editor-error';
        var actions = put(content, 'div', 'toolbar');
        function commit(playVideo) {
            try {
                var safe = core.videoURL(url.value), saved;
                if (item) { item.url = safe; item.title = core.cleanText(title.value, 90) || 'Saved video'; saved = item; }
                else { saved = core.add(data, title.value, safe); }
                persist(); content.className = '';
                if (playVideo) { start(saved, true); } else { library(false); notice('Video saved.'); }
            } catch (problem) { error.textContent = problem.message; }
        }
        button(actions, 'Save & play', function () { commit(true); }); button(actions, 'Save', function () { commit(false); });
        button(actions, 'Cancel', function () { home(); });
        editingField = 'url'; caps = false; url.focus();
    }
    function about() {
        begin('about', 'A useful app. Honest limits.', 'Legacy TV Hub preview 0.1 — a shared app for older TV browsers, with platform-specific installers.');
        var toolbar = put(content, 'div', 'toolbar');
        button(toolbar, data.contrast ? 'Contrast: high' : 'Contrast: standard', function () {
            data.contrast = !data.contrast; document.body.className = data.contrast ? 'high-contrast' : ''; persist(); about();
        }); button(toolbar, 'Home', home);
        put(content, 'p', 'notice-box', 'This app uses the TV’s existing player. It does not replace the operating system or enable Paramount+ or other unsupported subscription services.');
        var boxes = put(content, 'div', 'info-grid'), box = put(boxes, 'div', 'info-box');
        put(box, 'h2', '', 'Saved on this device'); put(box, 'p', '', persistent ? 'Your library and watch positions are stored locally. No account or tracking.' : 'Storage is unavailable. Your changes last for this session.');
        box = put(boxes, 'div', 'info-box'); put(box, 'h2', '', 'Video support'); put(box, 'p', '', 'H.264 MP4: ' + (video.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"') || 'not advertised') + '. Playback depends on the link, codec and the TV.');
        box = put(boxes, 'div', 'info-box'); put(box, 'h2', '', 'Controls'); put(box, 'p', '', 'Arrows and OK move around the app. Return goes back. During playback, Left/Right seek and OK pauses.');
        box = put(boxes, 'div', 'info-box'); put(box, 'h2', '', platform ? platform.name : 'Browser preview'); put(box, 'p', '', navigator.userAgent);
        focusFirst();
    }
    function demo() { start({id: 'demo', title: 'Offline playback demo', url: 'media/demo.mp4', position: 0, duration: 10, played: 0}, true); }
    function remember(force) {
        if (!active || active.id === 'demo') { return; }
        var now = new Date().getTime();
        if (!force && now - lastSave < 5000) { return; }
        lastSave = now;
        if (isFinite(video.currentTime)) { active.position = Math.max(0, video.currentTime); }
        if (isFinite(video.duration)) { active.duration = Math.max(0, video.duration); }
        active.played = now; persist();
    }
    function play() {
        try {
            var promise = video.play();
            if (promise && typeof promise['catch'] === 'function') { promise['catch'](function () { state('Press Play to begin.'); }); }
        } catch (problem) { state('This video could not be started.'); }
    }
    function state(text) { document.getElementById('player-state').textContent = text; }
    function toggle() { if (video.paused || video.ended) { play(); } else { video.pause(); } }
    function seek(amount) {
        try { if (isFinite(video.duration)) { video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + amount)); } }
        catch (ignored) { state('Seeking unavailable for this video.'); }
    }
    function closePlayer() {
        remember(true); video.pause(); video.removeAttribute('src'); video.load(); active = null;
        document.getElementById('player-screen').className = 'hidden'; document.getElementById('shell').className = ''; home();
    }
    function start(item, fromBeginning) {
        active = item; resume = fromBeginning ? 0 : core.resumeAt(item); lastSave = 0; view = 'player';
        content.className = ''; document.getElementById('shell').className = 'hidden'; document.getElementById('player-screen').className = '';
        document.getElementById('player-title').textContent = item.title;
        var controls = document.getElementById('player-buttons'); controls.innerHTML = '';
        button(controls, 'Play / pause', toggle); button(controls, '−10 seconds', function () { seek(-10); }); button(controls, '+10 seconds', function () { seek(10); }); button(controls, 'Close', closePlayer);
        state('Loading…'); video.src = item.url; video.load(); play(); focusFirst();
    }
    function block(event) {
        if (event.preventDefault) { event.preventDefault(); }
        try { if (platform && platform.blockNavigation) { platform.blockNavigation(event); } } catch (ignored) {}
    }
    function onKey(event) {
        var code = event.keyCode || event.which, name, input = document.activeElement && document.activeElement.tagName === 'INPUT';
        if (code === keys.EXIT && platform && platform.exit) { remember(true); video.pause(); block(event); platform.exit(); return; }
        if (view === 'player') {
            if (code === keys.RETURN || code === 27) { block(event); closePlayer(); }
            else if (code === keys.ENTER || code === 32) { block(event); toggle(); }
            else if (code === keys.LEFT || code === keys.REW) { block(event); seek(-10); }
            else if (code === keys.RIGHT || code === keys.FF) { block(event); seek(10); }
            else if (code === keys.PLAY) { block(event); play(); }
            else if (code === keys.PAUSE) { block(event); video.pause(); }
            else if (code === keys.STOP) { block(event); closePlayer(); }
            return;
        }
        if ((code === keys.RETURN && !(input && code === 8)) || code === 27) {
            if (view !== 'home') { block(event); home(); }
            else if (platform && platform.returnToHub) { block(event); platform.returnToHub(); }
            return;
        }
        for (name in keys) {
            if (keys.hasOwnProperty(name) && code === keys[name] && /^(UP|DOWN|LEFT|RIGHT)$/.test(name)) {
                if (input && (name === 'LEFT' || name === 'RIGHT')) { return; }
                block(event); move(name); return;
            }
        }
        if (code === keys.ENTER && !input && document.activeElement && document.activeElement.tagName === 'BUTTON') { block(event); document.activeElement.click(); }
    }
    function fit() {
        var scale = Math.min(window.innerWidth / 1280, window.innerHeight / 720), shell = document.getElementById('shell');
        shell.style.webkitTransform = 'scale(' + scale + ')'; shell.style.transform = 'scale(' + scale + ')';
        shell.style.left = Math.max(0, (window.innerWidth - 1280 * scale) / 2) + 'px'; shell.style.top = Math.max(0, (window.innerHeight - 720 * scale) / 2) + 'px';
    }
    function clock() { var now = new Date(), minutes = now.getMinutes(); document.getElementById('clock').textContent = now.getHours() + ':' + (minutes < 10 ? '0' : '') + minutes; }
    function init() {
        content = document.getElementById('content'); video = document.getElementById('video');
        try { store = window.localStorage; } catch (ignored) { store = null; }
        var loaded = core.load(store); data = loaded.data; persistent = loaded.persistent;
        try {
            if (window.HubPlatform) {
                platform = window.HubPlatform;
                nativeKeys = platform.keys();
                var name; for (name in keys) { if (keys.hasOwnProperty(name) && typeof nativeKeys[name] === 'number') { keys[name] = nativeKeys[name]; } }
                platform.ready();
            }
        } catch (ignoredNative) { platform = null; }
        video.addEventListener('loadedmetadata', function () { if (resume) { try { video.currentTime = resume; } catch (ignored) {} resume = 0; } }, false);
        video.addEventListener('playing', function () { state('Playing'); }, false);
        video.addEventListener('pause', function () { state(video.ended ? 'Finished' : 'Paused'); remember(true); }, false);
        video.addEventListener('waiting', function () { state('Buffering…'); }, false);
        video.addEventListener('ended', function () { state('Finished'); remember(true); }, false);
        video.addEventListener('error', function () { state('Cannot play this link on this TV. Return to choose another.'); }, false);
        video.addEventListener('timeupdate', function () {
            var duration = isFinite(video.duration) ? video.duration : 0;
            document.getElementById('play-time').textContent = core.time(video.currentTime) + ' / ' + core.time(duration);
            document.getElementById('played').style.width = (duration ? Math.max(0, Math.min(100, 100 * video.currentTime / duration)) : 0) + '%'; remember(false);
        }, false);
        document.addEventListener('keydown', onKey, false); window.onresize = fit;
        window.addEventListener('beforeunload', function () { remember(true); }, false);
        document.body.className = data.contrast ? 'high-contrast' : ''; home(); fit(); clock(); window.setInterval(clock, 30000);
        notice(persistent ? 'Stored locally. No account needed.' : 'Changes are kept for this session only.');
    }
    window.addEventListener('load', init, false);
}());
