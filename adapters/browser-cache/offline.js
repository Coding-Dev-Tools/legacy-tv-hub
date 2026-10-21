(function () {
    'use strict';
    var cache = window.applicationCache, label, message = 'Checking offline storage...';
    function show(text) {
        message = text;
        if (label) { label.textContent = text; }
    }
    window.addEventListener('load', function () {
        var release = document.querySelector('.release');
        if (!release) { return; }
        release.appendChild(document.createTextNode(' | '));
        label = document.createElement('span');
        label.id = 'offline-status';
        label.setAttribute('role', 'status');
        release.appendChild(label);
        show(message);
    }, false);
    if (!cache || typeof cache.addEventListener !== 'function') {
        show('Offline storage unavailable in this browser.');
        return;
    }
    cache.addEventListener('checking', function () { show('Checking offline copy...'); }, false);
    cache.addEventListener('downloading', function () { show('Saving offline copy...'); }, false);
    cache.addEventListener('cached', function () { show('Offline copy stored.'); }, false);
    cache.addEventListener('noupdate', function () { show('Offline copy ready.'); }, false);
    cache.addEventListener('updateready', function () {
        try { cache.swapCache(); show('Update saved. Reopen to use it.'); }
        catch (ignored) { show('Update ready. Reopen to use it.'); }
    }, false);
    cache.addEventListener('obsolete', function () { show('Offline copy removed by the host.'); }, false);
    cache.addEventListener('error', function () {
        show(cache.status === 1 ? 'Using saved copy; update check failed.' : 'Offline save failed. Hosting is still needed.');
    }, false);
}());
