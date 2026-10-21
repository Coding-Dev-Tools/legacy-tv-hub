"""Temporary preview / Legacy widget-sync server. No third-party packages or firewall changes."""
import argparse
import hashlib
import http.server
import ipaddress
import json
import mimetypes
import socket
import time
import threading
import secrets
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from tools.packaging import VERSION

ROOT = Path(__file__).resolve().parent

def widgetlist(host, port, release):
    root = ET.Element('rsp', stat='ok')
    item = ET.SubElement(ET.SubElement(root, 'list'), 'widget', id='LegacyTVHub')
    ET.SubElement(item, 'title').text = 'Legacy TV Hub'
    ET.SubElement(item, 'compression', size=str(release['bytes']), type='zip')
    ET.SubElement(item, 'description').text = 'Remote-friendly direct video player. Preview; not firmware.'
    ET.SubElement(item, 'download').text = 'http://' + host + (':' + str(port) if port != 80 else '') + '/Widget/' + release['archive']
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Bind localhost for a desktop browser preview')
    parser.add_argument('--offline', action='store_true', help='Serve the verified optional AppCache build from dist/offline')
    parser.add_argument('--setup', action='store_true', help='Build the offline copy and open it on the identified Samsung TV')
    parser.add_argument('--expected-model', default='UN55HU7250', help='Exact expected model for --setup; only UN55HU7250 has physical-browser evidence')
    parser.add_argument('--tv', help='TV IPv4 address; required for a local-network installation server')
    parser.add_argument('--port', type=int, help='Default: 8766 for preview; 8769 for offline/setup; 80 for TV sync')
    parser.add_argument('--duration', type=int, default=900, help='Server lifetime in seconds, up to 3600')
    args = parser.parse_args()
    if args.setup and (args.preview or not args.tv):
        parser.error('--setup requires --tv and cannot be combined with --preview')
    if args.setup:
        args.offline = True
    if not 1 <= args.duration <= 3600:
        parser.error('Duration must be between 1 and 3600 seconds')
    if args.preview:
        bind = '127.0.0.1'
        allowed = {'127.0.0.1'}
    else:
        if not args.tv:
            parser.error('Use --tv with the TV address, or use --preview')
        from tools.samsung_legacy_browser import television_address
        try:
            args.tv = television_address(args.tv)
        except ValueError:
            parser.error('The TV must have a private local IPv4 address')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.connect((args.tv, 9))  # Select an interface without sending a packet.
            bind = connection.getsockname()[0]
        if not ipaddress.ip_address(bind).is_private:
            parser.error('No private local interface selected')
        allowed = {args.tv, bind, '127.0.0.1'}
    port = args.port if args.port is not None else (8766 if args.preview else (8769 if args.offline else 80))
    if not 1 <= port <= 65535:
        parser.error('Invalid port')
    release, package, manifest = None, None, None
    if args.offline:
        from tools.build_offline_web import build, verified_files
        if args.setup:
            build(ROOT / 'dist' / 'offline')
        try:
            app_files = verified_files(ROOT / 'dist' / 'offline')
        except (OSError, ValueError):
            parser.error('Offline copy missing or changed. Run python tools/build_offline_web.py or use --setup.')
    else:
        release = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
        package = ROOT / release['archive']
        if package.parent != ROOT or not package.is_file() or hashlib.sha256(package.read_bytes()).hexdigest() != release['sha256']:
            raise RuntimeError('Package checksum mismatch; rebuild with build.py before serving')
        app_files = {'/' + path.relative_to(ROOT / 'app').as_posix(): path for path in (ROOT / 'app').rglob('*') if path.is_file()}
        app_files['/'] = ROOT / 'app' / 'index.html'
        manifest = widgetlist(bind, port, release)
    counts = {'widgetlist_requests': 0, 'package_requests': 0}
    setup_ready = threading.Event()
    setup_token = secrets.token_hex(16) if args.setup else None
    setup_origin = 'http://' + bind + (':' + str(port) if port != 80 else '')

    class Handler(http.server.BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(8)
        def log_message(self, *unused):
            pass
        def do_HEAD(self):
            self.send_file(False)
        def do_GET(self):
            self.send_file(True)
        def do_POST(self):
            parsed = urllib.parse.urlsplit(self.path)
            if not args.setup or parsed.path != '/_setup/ready':
                self.send_error(404)
                return
            if (self.client_address[0] != args.tv or self.headers.get('Origin') != setup_origin or
                    urllib.parse.parse_qs(parsed.query).get('run') != [setup_token]):
                self.send_error(403)
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 256:
                    raise ValueError()
                data = json.loads(self.rfile.read(size))
                if data != {'version': VERSION}:
                    raise ValueError()
            except (ValueError, TypeError):
                self.send_error(400)
                return
            self.send_response(204)
            self.send_header('Content-Length', '0')
            self.end_headers()
            print('TV confirmed offline copy stored / ready for version ' + VERSION + '.', flush=True)
            setup_ready.set()
        def send_file(self, body):
            if self.client_address[0] not in allowed:
                self.send_error(403)
                return
            path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
            if path == '/widgetlist.xml' and manifest is not None:
                counts['widgetlist_requests'] += 1
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml; charset=utf-8')
                self.send_header('Content-Length', str(len(manifest)))
                self.end_headers()
                if body:
                    self.wfile.write(manifest)
                return
            file = package if package is not None and path == '/Widget/' + release['archive'] else app_files.get(path)
            if not file:
                self.send_error(404)
                return
            if file == package:
                counts['package_requests'] += 1
            start, end = 0, file.stat().st_size - 1
            header = self.headers.get('Range', '')
            if header:
                try:
                    if not header.startswith('bytes='):
                        raise ValueError()
                    left, right = header[6:].split('-', 1)
                    if not left:
                        suffix = int(right)
                        if suffix <= 0:
                            raise ValueError()
                        start = max(0, file.stat().st_size-suffix)
                    else:
                        start = int(left)
                        end = min(end, int(right) if right else end)
                    if start < 0 or end < start or start >= file.stat().st_size:
                        raise ValueError()
                except ValueError:
                    self.send_error(416)
                    return
            self.send_response(206 if header else 200)
            self.send_header('Content-Type', 'text/cache-manifest' if file.suffix == '.appcache' else (mimetypes.guess_type(file)[0] or 'application/octet-stream'))
            self.send_header('Content-Length', str(end-start+1))
            self.send_header('Accept-Ranges', 'bytes')
            if args.offline:
                self.send_header('Cache-Control', 'no-cache')
            if header:
                self.send_header('Content-Range', 'bytes ' + str(start) + '-' + str(end) + '/' + str(file.stat().st_size))
            self.end_headers()
            if body:
                try:
                    with file.open('rb') as stream:
                        stream.seek(start)
                        remaining = end-start+1
                        while remaining:
                            chunk = stream.read(min(65536, remaining))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError, TimeoutError):
                    pass
    try:
        server = http.server.ThreadingHTTPServer((bind, port), Handler)
    except OSError as error:
        parser.exit(1, 'Cannot listen on the selected interface/port (' + type(error).__name__ + '). Try another port for browser setup.\n')
    server.timeout = 1
    server.daemon_threads = True
    print('Temporary server: http://' + bind + ':' + str(port) + '/', flush=True)
    if args.offline:
        print('Offline browser copy: wait for the TV to report that the copy is stored before stopping this server. This is not native installation.', flush=True)
    if not args.preview and not args.offline:
        print('Legacy User App Sync server IP: ' + bind + '. Port 80 is required by the documented TV flow.', flush=True)
    print('Stops in ' + str(args.duration) + ' seconds. Ctrl+C also stops it. No installation is triggered by this script.', flush=True)
    launch_failed = threading.Event()
    launcher = None
    if args.setup:
        def open_browser():
            from tools.samsung_legacy_browser import launch
            try:
                result = launch(args.tv, setup_origin + '/#setup=' + setup_token, args.expected_model)
                print('Browser launch accepted; waiting for the TV to confirm its offline copy. No account or library data is reported.', flush=True)
                print(json.dumps(result), flush=True)
            except (OSError, ValueError, ET.ParseError) as error:
                print('Browser launch failed (' + type(error).__name__ + '). No TV software was changed.', flush=True)
                launch_failed.set()
        launcher = threading.Thread(target=open_browser, daemon=True)
        launcher.start()
    deadline = time.monotonic() + args.duration
    try:
        while time.monotonic() < deadline and not launch_failed.is_set() and not setup_ready.is_set():
            server.handle_request()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if launcher:
            launcher.join(timeout=9)
        print('Server stopped. Sync request counts: ' + json.dumps(counts), flush=True)
    if args.setup and not launch_failed.is_set():
        if not setup_ready.is_set():
            print('The TV did not confirm storage before the timeout. Reopen the app if an update was saved, or open the printed URL manually. Setup remains unverified.', flush=True)
            return 1
        try:
            from tools.samsung_legacy_browser import launch
            launch(args.tv, setup_origin + '/', args.expected_model)
            print('Reopen requested with the asset server stopped. Bookmark ' + setup_origin + '/ on the TV. A launch response alone does not verify the reopened page or a TV power cycle.', flush=True)
        except (OSError, ValueError, ET.ParseError) as error:
            print('Offline copy stored, but the reopen request failed (' + type(error).__name__ + '). Reopen the bookmarked URL on the TV.', flush=True)
            return 1
    return 1 if launch_failed.is_set() else 0

if __name__ == '__main__':
    raise SystemExit(main())
