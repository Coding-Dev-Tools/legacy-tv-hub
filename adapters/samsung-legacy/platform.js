/* Samsung Legacy adapter. Loaded only in its native user-widget package. */
(function (root) {
    'use strict';
    var widget, nativeKeys;
    if (!root.Common || !Common.API) { return; }
    widget = new Common.API.Widget(); nativeKeys = new Common.API.TVKeyValue();
    root.HubPlatform = {
        name: 'Samsung Legacy app',
        keys: function () {
            var output = {}, names = ['UP','DOWN','LEFT','RIGHT','ENTER','RETURN','EXIT','PLAY','PAUSE','STOP','FF'], i;
            for (i = 0; i < names.length; i += 1) { output[names[i]] = nativeKeys['KEY_' + names[i]]; }
            output.REW = typeof nativeKeys.KEY_RW === 'number' ? nativeKeys.KEY_RW : nativeKeys.KEY_REW;
            return output;
        },
        ready: function () { widget.sendReadyEvent(); },
        createTVPlayer: function (notify) {
            if (!root.HubLegacyPlayer) { throw new Error('TV player adapter is unavailable.'); }
            return root.HubLegacyPlayer.create(document.getElementById('hub-native-player'), notify);
        },
        runtimeInfo: function () {
            var info = {firmware: 'Unavailable', systemVersion: 'Unavailable'}, plugin;
            try {
                plugin = document.getElementById('hub-native-info');
                if (plugin.Open('NNavi', '1.016', 'NNavi') === false) { return info; }
                var firmware = plugin.Execute('GetFirmware');
                if (typeof firmware === 'string' && /^T-[A-Za-z0-9_.-]{1,90}$/.test(firmware)) { info.firmware = firmware; }
                var systemVersion = plugin.Execute('GetSystemVersion', 0);
                if (typeof systemVersion === 'string') { info.systemVersion = systemVersion.replace(/[\u0000-\u001f]/g, '').slice(0, 100); }
            } catch (ignored) {}
            return info;
        },
        blockNavigation: function (event) { widget.blockNavigation(event); },
        returnToHub: function () { widget.sendReturnEvent(); },
        exit: function () { widget.sendExitEvent(); }
    };
}(this));
