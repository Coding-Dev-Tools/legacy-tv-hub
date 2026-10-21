"""Shared release metadata and platform-independent ZIP attributes."""
from datetime import date
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
METADATA = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
VERSION = METADATA['version']
match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', VERSION)
if not match:
    raise ValueError('Use a numeric major.minor.patch release version.')
major, minor, patch = map(int, match.groups())
if minor > 9 or patch > 99:
    raise ValueError('The Legacy widget version requires minor <= 9 and patch <= 99.')
WIDGET_VERSION = f'{major}.{minor * 100 + patch:03d}'
RELEASE_DATE = date.fromisoformat(METADATA['tvHub']['releaseDate'])
ZIP_DATE = (RELEASE_DATE.year, RELEASE_DATE.month, RELEASE_DATE.day, 0, 0, 0)
VERSION_SCRIPT = ("/* Generated from package.json by build.py. */\nwindow.HubVersion = '" + VERSION + "';\n").encode('utf-8')


def asset_bytes(path):
    if path.name == 'version.js':
        return VERSION_SCRIPT
    data = path.read_bytes()
    if path.suffix.lower() in {'.js', '.html', '.css', '.xml', '.json'} or path.name == 'LICENSE':
        data = data.replace(b'\r\n', b'\n')
    return data


def entry(name):
    info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info
