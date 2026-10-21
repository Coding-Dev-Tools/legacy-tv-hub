"""Build an optional HTML5 AppCache copy for browsers that still support it.

This caches the app and bundled clip. It cannot install a native widget, replace
firmware, add a DRM system or store arbitrary streaming-service movies.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.1'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def offline_files():
    app = ROOT / 'app'
    files = {path.relative_to(app).as_posix():path.read_bytes().replace(b'\r\n',b'\n')
             if path.suffix in {'.html','.js','.css'} else path.read_bytes()
             for path in sorted(app.rglob('*')) if path.is_file()}
    html = files['index.html'].decode('utf-8')
    if '<html lang="en">' not in html or '</body>' not in html:
        raise ValueError('Unexpected app entry document; no offline build written.')
    html = html.replace('<html lang="en">', '<html lang="en" manifest="manifest.appcache">', 1)
    html = html.replace('</body>', '<script src="offline.js"></script></body>', 1)
    files['index.html'] = html.encode('utf-8')
    files['offline.js'] = (ROOT/'adapters/browser-cache/offline.js').read_bytes().replace(b'\r\n',b'\n')
    hashes = {name:digest(data) for name,data in files.items()}
    build_id = digest(json.dumps(hashes,sort_keys=True).encode('utf-8'))
    files['manifest.appcache'] = ('CACHE MANIFEST\n# Legacy TV Hub '+VERSION+' '+build_id+
        '\nCACHE:\n'+'\n'.join(sorted(files))+'\nNETWORK:\n*\n').encode('utf-8')
    return files

def build(output):
    output = Path(output).resolve()
    app = (ROOT/'app').resolve()
    if output == app or app in output.parents or output == ROOT:
        raise ValueError('Choose a separate offline output directory.')
    marker = output/'offline-build.json'
    if output.exists() and any(output.iterdir()):
        if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('format') != 'legacy-tv-hub-offline-v1':
            raise ValueError('Refusing to overwrite an unrelated nonempty directory.')
    files = offline_files()
    output.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        target = output.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    record = {'format':'legacy-tv-hub-offline-v1','version':VERSION,
              'files':{name:digest(data) for name,data in sorted(files.items())},
              'firmware':False,'native_installation':False,'enables_paramount_plus':False,
              'power_cycle_persistence_verified':False}
    marker.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    archive = output.parent/('LegacyTVHub_offline_web_'+VERSION+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as package:
        for name,data in sorted(files.items()):
            info = zipfile.ZipInfo(name,date_time=(2026,10,21,0,0,0))
            info.external_attr = 0o100644 << 16
            package.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    record['archive'] = {'name':archive.name,'bytes':archive.stat().st_size,'sha256':digest(archive.read_bytes())}
    marker.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record

def verified_files(output):
    output = Path(output).resolve()
    record = json.loads((output/'offline-build.json').read_text(encoding='utf-8'))
    if record.get('format') != 'legacy-tv-hub-offline-v1' or not isinstance(record.get('files'),dict):
        raise ValueError('Rebuild the offline copy before serving it.')
    files = {}
    for name,expected in record['files'].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or any(part in {'..','.'} for part in relative.parts) or '\\' in name or ':' in name:
            raise ValueError('Unsafe offline asset path.')
        target = output.joinpath(*relative.parts).resolve()
        if output not in target.parents or not target.is_file() or digest(target.read_bytes()) != expected:
            raise ValueError('Offline asset mismatch; rebuild before serving.')
        files['/'+name] = target
    if not all('/'+name in files for name in ['index.html','manifest.appcache','offline.js','core.js','app.js','style.css','media/demo.mp4']):
        raise ValueError('Offline build is incomplete.')
    files['/'] = files['/index.html']
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'dist/offline')
    args = parser.parse_args()
    record = build(args.output)
    print(json.dumps({'output':str(args.output.resolve()),'archive':record['archive'],
                      'note':'Optional browser cache. Native installation and Paramount+ are not enabled.'},indent=2))

if __name__ == '__main__':
    main()
