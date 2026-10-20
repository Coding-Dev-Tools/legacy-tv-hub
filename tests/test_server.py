import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hub_server', ROOT/'serve.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.process = subprocess.Popen([sys.executable, '-u', str(ROOT/'serve.py'), '--preview', '--port', str(cls.port), '--duration', '30'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        line = cls.process.stdout.readline()
        if not line.startswith('Temporary server:'):
            cls.process.terminate()
            raise RuntimeError('Test server did not start: '+line)
        cls.base = 'http://127.0.0.1:'+str(cls.port)
        cls.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.process.stdout.close()
    def get(self, path, headers=None, method=None):
        return self.opener.open(urllib.request.Request(self.base+path, headers=headers or {}, method=method), timeout=3)
    def test_preview_and_no_source_exposure(self):
        with self.get('/') as response:
            self.assertIn(b'Legacy TV Hub', response.read())
        for path in ('/../serve.py', '/%2e%2e/serve.py', '/release.json', '/.git/config'):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.get(path)
            self.assertEqual(error.exception.code, 404)
    def test_byte_ranges_and_head(self):
        clip = (ROOT/'app/media/demo.mp4').read_bytes()
        with self.get('/media/demo.mp4', {'Range': 'bytes=5-14'}) as response:
            self.assertEqual(response.status, 206)
            self.assertEqual(response.read(), clip[5:15])
        with self.get('/media/demo.mp4', {'Range': 'bytes=-10'}) as response:
            self.assertEqual(response.read(), clip[-10:])
        with self.get('/media/demo.mp4', method='HEAD') as response:
            self.assertEqual(int(response.headers['Content-Length']), len(clip))
            self.assertEqual(response.read(), b'')
    def test_sync_manifest_and_archive(self):
        release = json.loads((ROOT/'release.json').read_text(encoding='utf-8'))
        with self.get('/widgetlist.xml') as response:
            manifest = ET.fromstring(response.read())
        self.assertEqual(manifest.find('.//widget').get('id'), 'LegacyTVHub')
        self.assertEqual(int(manifest.find('.//compression').get('size')), release['bytes'])
        self.assertTrue(manifest.findtext('.//download').endswith('/Widget/'+release['archive']))
        with zipfile.ZipFile(ROOT/release['archive']) as package:
            self.assertIsNone(package.testzip())
            self.assertIn('platform-native.js', package.namelist())
            self.assertIn('$MANAGER_WIDGET', package.read('index.html').decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
