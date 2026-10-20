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
        blockNavigation: function (event) { widget.blockNavigation(event); },
        returnToHub: function () { widget.sendReturnEvent(); },
        exit: function () { widget.sendExitEvent(); }
    };
}(this));
