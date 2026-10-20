"""Build a reproducible Legacy user-widget ZIP using Python's standard library."""
import hashlib
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'app'
ARCHIVE = ROOT / 'LegacyTVHub_0.200_USA_20261020.zip'
WEB_ARCHIVE = ROOT / 'LegacyTVHub_portable_web_0.2.0.zip'
NATIVE_SCRIPTS = ('<script src="$MANAGER_WIDGET/Common/API/Widget.js"></script>'
                  '<script src="$MANAGER_WIDGET/Common/API/TVKeyValue.js"></script>'
                  '<script src="legacy-player.js"></script><script src="platform-native.js"></script>')
NATIVE_OBJECTS = ('<object id="hub-native-player" classid="clsid:SAMSUNG-INFOLINK-PLAYER" style="position:absolute;width:0;height:0"></object>'
                  '<object id="hub-native-info" classid="clsid:SAMSUNG-INFOLINK-SEF" style="position:absolute;width:0;height:0"></object>')

def asset_bytes(path):
    data = path.read_bytes()
    if path.suffix.lower() in {'.js', '.html', '.css', '.xml', '.json'}:
        data = data.replace(b'\r\n', b'\n')
    return data

def build():
    adapter = ROOT / 'adapters' / 'samsung-legacy'
    config = ET.parse(adapter / 'config.xml').getroot()
    assert config.findtext('{*}type') == 'user'
    assert config.findtext('{*}widgetname') == 'LegacyTVHub'
    assert config.findtext('{*}ver') == '0.200'
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        source_files = [(path, path.relative_to(APP).as_posix()) for path in sorted(APP.rglob('*')) if path.is_file()]
        source_files += [(adapter / 'config.xml', 'config.xml'), (adapter / 'platform.js', 'platform-native.js'), (adapter / 'player.js', 'legacy-player.js')]
        for path, name in source_files:
            if not path.is_file():
                continue
            data = asset_bytes(path)
            if name == 'index.html':
                data = data.decode('utf-8').replace('<script src="core.js">', NATIVE_SCRIPTS + '<script src="core.js">').encode('utf-8')
                data = data.decode('utf-8').replace('<div id="shell">', NATIVE_OBJECTS + '<div id="shell">').encode('utf-8')
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        files = archive.namelist()
        assert all(name in files for name in ('config.xml', 'index.html', 'app.js', 'core.js', 'style.css', 'media/demo.mp4'))
    with zipfile.ZipFile(WEB_ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(APP.rglob('*')):
            if path.is_file():
                entry = zipfile.ZipInfo(path.relative_to(APP).as_posix(), date_time=(2026, 10, 20, 0, 0, 0))
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, asset_bytes(path), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    manifest = {'name': 'Legacy TV Hub', 'version': '0.200', 'archive': ARCHIVE.name,
                'bytes': ARCHIVE.stat().st_size, 'sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                'platform_target': 'Samsung 2014 Legacy user application',
                'release_status': 'Preview. Native installation, HTML playback and the optional Samsung PLAYER adapter require physical-TV validation.',
                'firmware': False, 'enables_paramount_plus': False, 'permanent_pc_required_after_native_install': False}
    manifest['portable_web'] = {'archive': WEB_ARCHIVE.name, 'bytes': WEB_ARCHIVE.stat().st_size,
                                'sha256': hashlib.sha256(WEB_ARCHIVE.read_bytes()).hexdigest(),
                                'status': 'Browser app; requires a compatible browser and independent hosting or a native installation adapter.'}
    (ROOT / 'release.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    build()
