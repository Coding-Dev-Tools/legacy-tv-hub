import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('offline_builder',ROOT/'tools/build_offline_web.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class OfflineBuildTests(unittest.TestCase):
    def test_archive_covers_cache_resources_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'offline'
            first = builder.build(output)
            second = builder.build(output)
            self.assertEqual(first['archive']['sha256'],second['archive']['sha256'])
            self.assertFalse(second['firmware'])
            self.assertFalse(second['enables_paramount_plus'])
            with zipfile.ZipFile(output.parent/second['archive']['name']) as archive:
                self.assertIsNone(archive.testzip())
                html = archive.read('index.html').decode('utf-8')
                self.assertIn('manifest="manifest.appcache"',html)
                self.assertIn('src="offline.js"',html)
                manifest = archive.read('manifest.appcache').decode('utf-8')
                listed = manifest.split('CACHE:\n',1)[1].split('\nNETWORK:',1)[0].splitlines()
                for name in listed:
                    self.assertIn(name,archive.namelist())
                self.assertIn('media/demo.mp4',listed)
                self.assertNotIn('offline-build.json',archive.namelist())
            builder.verified_files(output)

    def test_modified_asset_and_traversal_are_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'offline'
            builder.build(output)
            (output/'app.js').write_text('tampered',encoding='utf-8')
            with self.assertRaises(ValueError): builder.verified_files(output)
            record = builder.build(output)
            record['files']['../outside.txt'] = '0'*64
            (output/'offline-build.json').write_text(json.dumps(record),encoding='utf-8')
            with self.assertRaises(ValueError): builder.verified_files(output)

    def test_unrelated_directory_and_source_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output/'keep.txt').write_text('keep',encoding='utf-8')
            with self.assertRaises(ValueError): builder.build(output)
            self.assertEqual((output/'keep.txt').read_text(encoding='utf-8'),'keep')
        with self.assertRaises(ValueError): builder.build(ROOT/'app')

class OfflineHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder.build(ROOT/'dist/offline')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port = sock.getsockname()[1]
        cls.process = subprocess.Popen([sys.executable,'-u',str(ROOT/'serve.py'),'--preview','--offline','--port',str(port),'--duration','30'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        line = cls.process.stdout.readline()
        if not line.startswith('Temporary server:'):
            cls.process.terminate()
            raise RuntimeError('Offline server did not start: '+line)
        cls.base = 'http://127.0.0.1:'+str(port)
        cls.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.process.stdout.close()

    def test_manifest_type_and_all_resources_are_reachable(self):
        with self.opener.open(self.base+'/manifest.appcache',timeout=3) as response:
            self.assertEqual(response.headers.get_content_type(),'text/cache-manifest')
            self.assertEqual(response.headers['Cache-Control'],'no-cache')
            manifest = response.read().decode('utf-8')
        resources = manifest.split('CACHE:\n',1)[1].split('\nNETWORK:',1)[0].splitlines()
        for name in resources:
            request = urllib.request.Request(self.base+'/'+name,method='HEAD')
            with self.opener.open(request,timeout=3) as response:
                self.assertEqual(response.status,200)
                self.assertGreater(int(response.headers['Content-Length']),0)
        for path in ['/offline-build.json','/widgetlist.xml','/.git/config','/%2e%2e/serve.py']:
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.opener.open(self.base+path,timeout=3)
            self.assertEqual(error.exception.code,404)

    def test_video_range_is_preserved(self):
        request = urllib.request.Request(self.base+'/media/demo.mp4',headers={'Range':'bytes=100-199'})
        with self.opener.open(request,timeout=3) as response:
            self.assertEqual(response.status,206)
            self.assertEqual(response.read(),(ROOT/'app/media/demo.mp4').read_bytes()[100:200])

if __name__ == '__main__':
    unittest.main()
