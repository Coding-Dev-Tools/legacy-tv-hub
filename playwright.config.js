'use strict';
const {defineConfig} = require('@playwright/test');
module.exports = defineConfig({
    testDir: './tests/browser',
    timeout: 30000,
    workers: 1,
    use: {baseURL: 'http://127.0.0.1:8766', browserName: 'chromium', channel: process.env.HUB_BROWSER_CHANNEL || 'chrome', headless: true, viewport: {width: 1280, height: 720}},
    webServer: {command: '"' + (process.env.HUB_PYTHON || 'python') + '" serve.py --preview --duration 300', url: 'http://127.0.0.1:8766', reuseExistingServer: false, timeout: 15000}
});
