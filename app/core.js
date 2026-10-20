/* Legacy TV Hub. ES5 only; no network or browser dependencies in this module. */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) { module.exports = factory(); }
    else { root.HubCore = factory(); }
}(this, function () {
    'use strict';
    var KEY = 'legacy-tv-hub.v1';
    var MAX_ITEMS = 60;

    function cleanText(value, limit) {
        return String(value || '').replace(/[\u0000-\u001f\u007f]/g, '').replace(/^\s+|\s+$/g, '').slice(0, limit || 90);
    }
    function videoURL(value) {
        var text = cleanText(value, 4097);
        if (text.length > 4096 || !/^https?:\/\/[^\s/?#]+(?:[/?#][^\s]*)?$/i.test(text)) {
            throw new Error('Enter a full http:// or https:// video link, without spaces.');
        }
        var authority = text.replace(/^https?:\/\//i, '').split(/[/?#]/)[0];
        if (authority.indexOf('@') !== -1) { throw new Error('Links containing a username or password are not supported.'); }
        if (/[<>"\\]/.test(text)) { throw new Error('That link contains unsupported characters.'); }
        return text;
    }
    function empty() { return {version: 1, items: [], contrast: false}; }
    function seconds(value) { var number = Number(value); return isFinite(number) ? Math.max(0, number) : 0; }
    function normalize(data) {
        var output = empty(), rows = data && data.version === 1 && data.items, i, row, url, seen = {};
        output.contrast = !!(data && data.contrast);
        if (!rows || Object.prototype.toString.call(rows) !== '[object Array]') { return output; }
        for (i = 0; i < rows.length && output.items.length < MAX_ITEMS; i += 1) {
            row = rows[i];
            try { url = videoURL(row && row.url); } catch (ignored) { continue; }
            if (seen[url]) { continue; }
            seen[url] = true;
            output.items.push({
                id: 'video-' + output.items.length,
                title: cleanText(row.title, 90) || 'Saved video',
                url: url,
                position: seconds(row.position),
                duration: seconds(row.duration),
                played: seconds(row.played)
            });
        }
        return output;
    }
    function load(storage) {
        try { return {data: normalize(JSON.parse(storage.getItem(KEY))), persistent: true}; }
        catch (ignored) { return {data: empty(), persistent: false}; }
    }
    function save(storage, data) {
        try { storage.setItem(KEY, JSON.stringify(normalize(data))); return true; }
        catch (ignored) { return false; }
    }
    function add(data, title, url) {
        var safeURL = videoURL(url), i, row;
        for (i = 0; i < data.items.length; i += 1) {
            if (data.items[i].url === safeURL) {
                data.items[i].title = cleanText(title, 90) || data.items[i].title;
                return data.items[i];
            }
        }
        if (data.items.length >= MAX_ITEMS) { throw new Error('Your library is full. Remove a video before adding another.'); }
        row = {id: 'video-' + String(new Date().getTime()), title: cleanText(title, 90) || 'Saved video', url: safeURL, position: 0, duration: 0, played: 0};
        data.items.push(row);
        return row;
    }
    function resumeAt(item) {
        var position = Number(item.position), duration = Number(item.duration);
        return isFinite(position) && isFinite(duration) && duration > 15 && position >= 5 && position < duration - 5 ? position : 0;
    }
    function time(seconds) {
        var value = Math.max(0, Math.floor(Number(seconds) || 0));
        if (!isFinite(value)) { value = 0; }
        return Math.floor(value / 60) + ':' + (value % 60 < 10 ? '0' : '') + value % 60;
    }
    return {key: KEY, maxItems: MAX_ITEMS, empty: empty, normalize: normalize, load: load, save: save, add: add, videoURL: videoURL, cleanText: cleanText, resumeAt: resumeAt, time: time};
}));
