"""Build a reproducible Legacy user-widget ZIP using Python's standard library."""
import hashlib
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from tools.packaging import VERSION, WIDGET_VERSION, RELEASE_DATE, VERSION_SCRIPT, asset_bytes, entry

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'app'
ARCHIVE = ROOT / ('LegacyTVHub_' + WIDGET_VERSION + '_USA_' + RELEASE_DATE.strftime('%Y%m%d') + '.zip')
WEB_ARCHIVE = ROOT / ('LegacyTVHub_portable_web_' + VERSION + '.zip')
NATIVE_SCRIPTS = ('<script src="$MANAGER_WIDGET/Common/API/Widget.js"></script>'
                  '<script src="$MANAGER_WIDGET/Common/API/TVKeyValue.js"></script>'
                  '<script src="legacy-player.js"></script><script src="platform-native.js"></script>')
NATIVE_OBJECTS = ('<object id="hub-native-player" classid="clsid:SAMSUNG-INFOLINK-PLAYER" style="position:absolute;width:0;height:0"></object>'
                  '<object id="hub-native-info" classid="clsid:SAMSUNG-INFOLINK-SEF" style="position:absolute;width:0;height:0"></object>')

def build():
    (APP / 'version.js').write_bytes(VERSION_SCRIPT)
    adapter = ROOT / 'adapters' / 'samsung-legacy'
    config = ET.parse(adapter / 'config.xml').getroot()
    assert config.findtext('{*}type') == 'user'
    assert config.findtext('{*}widgetname') == 'LegacyTVHub'
    config.find('{*}ver').text = WIDGET_VERSION
    ET.register_namespace('', 'http://www.samsung.com/')
    config_data = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        source_files = [(path, path.relative_to(APP).as_posix()) for path in sorted(APP.rglob('*')) if path.is_file()]
        source_files += [(adapter / 'config.xml', 'config.xml'), (adapter / 'platform.js', 'platform-native.js'), (adapter / 'player.js', 'legacy-player.js')]
        for path, name in sorted(source_files, key=lambda item: item[1]):
            if not path.is_file():
                continue
            data = asset_bytes(path)
            if name == 'config.xml':
                data = config_data
            if name == 'index.html':
                data = data.decode('utf-8').replace('<script src="core.js">', NATIVE_SCRIPTS + '<script src="core.js">').encode('utf-8')
                data = data.decode('utf-8').replace('<div id="shell">', NATIVE_OBJECTS + '<div id="shell">').encode('utf-8')
            archive.writestr(entry(name), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        files = archive.namelist()
        assert all(name in files for name in ('config.xml', 'index.html', 'app.js', 'core.js', 'style.css', 'media/demo.mp4'))
    with zipfile.ZipFile(WEB_ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(APP.rglob('*'), key=lambda path: path.relative_to(APP).as_posix()):
            if path.is_file():
                archive.writestr(entry(path.relative_to(APP).as_posix()), asset_bytes(path), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    manifest = {'name': 'Legacy TV Hub', 'version': VERSION, 'widget_version': WIDGET_VERSION, 'archive': ARCHIVE.name,
                'bytes': ARCHIVE.stat().st_size, 'sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                'platform_target': 'Samsung 2014 Legacy user application',
                'release_status': 'Preview. Native installation and the optional Samsung PLAYER adapter remain unverified. See docs/verification.md for browser test evidence.',
                'firmware': False, 'enables_paramount_plus': False, 'permanent_pc_required_after_native_install': False}
    manifest['portable_web'] = {'archive': WEB_ARCHIVE.name, 'bytes': WEB_ARCHIVE.stat().st_size,
                                'sha256': hashlib.sha256(WEB_ARCHIVE.read_bytes()).hexdigest(),
                                'status': 'Browser app; requires a compatible browser and independent hosting or a native installation adapter.'}
    from tools.build_offline_web import build as build_offline
    offline = build_offline(ROOT / 'dist' / 'offline')
    manifest['offline_web'] = dict(offline['archive'], status='Optional AppCache browser copy; persistence across a TV power cycle remains unverified.')
    checksums = [(ARCHIVE.name, manifest['sha256']), (WEB_ARCHIVE.name, manifest['portable_web']['sha256']),
                 (offline['archive']['name'], offline['archive']['sha256'])]
    (ROOT / 'SHA256SUMS').write_bytes(''.join(digest + '  ' + name + '\n' for name, digest in checksums).encode('ascii'))
    (ROOT / 'release.json').write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    build()
