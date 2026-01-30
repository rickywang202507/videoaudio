// Stealth Injector - Anti-Bot Detection Script
// This script removes common automation detection markers

(function () {
    'use strict';

    // 1. Remove webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // 2. Override Chrome automation properties
    window.chrome = window.chrome || {};
    Object.defineProperty(window.chrome, 'runtime', {
        get: () => ({})
    });

    // 3. Mock plugins to look like a real browser
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: { type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format" },
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format" },
                description: "Portable Document Format",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            },
            {
                0: { type: "application/x-nacl", suffixes: "", description: "Native Client Executable" },
                1: { type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable" },
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }
        ]
    });

    // 4. Mock languages to look natural
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'zh-CN', 'zh']
    });

    // 5. Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );

    // 6. Mock battery API
    Object.defineProperty(navigator, 'getBattery', {
        get: () => () => Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1.0
        })
    });

    // 7. Override toString to hide modifications
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function () {
        if (this === navigator.permissions.query) {
            return 'function query() { [native code] }';
        }
        if (this === navigator.getBattery) {
            return 'function getBattery() { [native code] }';
        }
        return originalToString.call(this);
    };

    // 8. Remove automation-related window properties
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

    // 9. Mock connection speed
    Object.defineProperty(navigator, 'connection', {
        get: () => ({
            effectiveType: '4g',
            downlink: 10,
            rtt: 50,
            saveData: false
        })
    });

    // 10. Mock hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8
    });

    // 11. Mock device memory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8
    });

    console.log('[Stealth] Anti-detection measures applied successfully');
})();
