"""Temporary preview / Legacy widget-sync server. No third-party packages or firewall changes."""
import argparse
import hashlib
import http.server
import ipaddress
import json
import mimetypes
import socket
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

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
    parser.add_argument('--tv', help='TV IPv4 address; required for a local-network installation server')
    parser.add_argument('--port', type=int, help='Default: 8766 for preview; 80 for TV sync')
    parser.add_argument('--duration', type=int, default=900, help='Server lifetime in seconds, up to 3600')
    args = parser.parse_args()
    if not 1 <= args.duration <= 3600:
        parser.error('Duration must be between 1 and 3600 seconds')
    if args.preview:
        bind = '127.0.0.1'
        allowed = {'127.0.0.1'}
    else:
        if not args.tv:
            parser.error('Use --tv with the TV address, or use --preview')
        address = ipaddress.ip_address(args.tv)
        if address.version != 4 or not address.is_private or address.is_loopback:
            parser.error('The TV must have a private local IPv4 address')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.connect((args.tv, 9))  # Select an interface without sending a packet.
            bind = connection.getsockname()[0]
        if not ipaddress.ip_address(bind).is_private:
            parser.error('No private local interface selected')
        allowed = {args.tv, bind, '127.0.0.1'}
    port = args.port or (8766 if args.preview else 80)
    if not 1 <= port <= 65535:
        parser.error('Invalid port')
    release, package, manifest = None, None, None
    if args.offline:
        from tools.build_offline_web import verified_files
        app_files = verified_files(ROOT / 'dist' / 'offline')
    else:
        release = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
        package = ROOT / release['archive']
        if package.parent != ROOT or not package.is_file() or hashlib.sha256(package.read_bytes()).hexdigest() != release['sha256']:
            raise RuntimeError('Package checksum mismatch; rebuild with build.py before serving')
        app_files = {'/' + path.relative_to(ROOT / 'app').as_posix(): path for path in (ROOT / 'app').rglob('*') if path.is_file()}
        app_files['/'] = ROOT / 'app' / 'index.html'
        manifest = widgetlist(bind, port, release)
    counts = {'widgetlist_requests': 0, 'package_requests': 0}

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
    server = http.server.ThreadingHTTPServer((bind, port), Handler)
    server.timeout = 1
    server.daemon_threads = True
    print('Temporary server: http://' + bind + ':' + str(port) + '/', flush=True)
    if args.offline:
        print('Offline browser copy: wait for the TV to report that the copy is stored before stopping this server. This is not native installation.', flush=True)
    if not args.preview and not args.offline:
        print('Legacy User App Sync server IP: ' + bind + '. Port 80 is required by the documented TV flow.', flush=True)
    print('Stops in ' + str(args.duration) + ' seconds. Ctrl+C also stops it. No installation is triggered by this script.', flush=True)
    deadline = time.monotonic() + args.duration
    try:
        while time.monotonic() < deadline:
            server.handle_request()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print('Server stopped. Sync request counts: ' + json.dumps(counts), flush=True)

if __name__ == '__main__':
    main()
