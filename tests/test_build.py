import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class ReleaseBuildTests(unittest.TestCase):
    def test_releases_are_reproducible_and_share_a_version(self):
        def build():
            subprocess.run([sys.executable, str(ROOT / 'build.py')], cwd=ROOT, check=True, capture_output=True)
            return json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
        first = build()
        second = build()
        self.assertEqual(first, second)
        version = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))['version']
        self.assertEqual(first['version'], version)
        self.assertIn(version.encode('ascii'), (ROOT / 'app/version.js').read_bytes())
        archives = [(ROOT / first['archive'], first['sha256']),
                    (ROOT / first['portable_web']['archive'], first['portable_web']['sha256']),
                    (ROOT / 'dist' / first['offline_web']['name'], first['offline_web']['sha256'])]
        checksums = (ROOT / 'SHA256SUMS').read_text(encoding='ascii')
        for path, expected in archives:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
            self.assertIn(expected + '  ' + path.name, checksums)
            with zipfile.ZipFile(path) as package:
                self.assertIsNone(package.testzip())
                self.assertIn(version.encode('ascii'), package.read('version.js'))
                self.assertTrue(all(info.create_system == 3 for info in package.infolist()))
                self.assertNotIn(b'\r\n', package.read('LICENSE'))
        with zipfile.ZipFile(archives[0][0]) as package:
            config = ET.fromstring(package.read('config.xml'))
            self.assertEqual(config.findtext('{*}ver'), first['widget_version'])


if __name__ == '__main__':
    unittest.main()
