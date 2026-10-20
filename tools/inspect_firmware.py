"""Read an MSDU10 firmware container offline. Does not decrypt, modify or install it."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys


class InvalidContainer(ValueError):
    pass


def read_exact(stream, count):
    data = stream.read(count)
    if len(data) != count:
        raise InvalidContainer('Truncated container header')
    return data


def inspect_stream(stream):
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)
    if read_exact(stream, 6) != b'MSDU10':
        raise InvalidContainer('Only MSDU10 is implemented; provide an extracted upgrade.msd')
    count, = struct.unpack('<I', read_exact(stream, 4))
    if not 1 <= count <= 512:
        raise InvalidContainer('Invalid or unsupported section count')
    sections = []
    for unused in range(count):
        section_id, offset, length = struct.unpack('<III', read_exact(stream, 12))
        sections.append({'id': section_id, 'offset': offset, 'bytes': length})
    if len({item['id'] for item in sections}) != count:
        raise InvalidContainer('Duplicate section identifiers')
    zero, toc_id, offset, length = struct.unpack('<IIII', read_exact(stream, 16))
    if zero != 0:
        raise InvalidContainer('Unexpected header separator')
    name_size = read_exact(stream, 1)[0]
    if name_size == 0:
        raise InvalidContainer('Missing declared model family')
    name = read_exact(stream, name_size)
    if any(byte < 32 or byte > 126 for byte in name):
        raise InvalidContainer('Model family is not printable ASCII')
    if read_exact(stream, 4) != b'\0' * 4:
        raise InvalidContainer('Unexpected model separator')
    header_end = stream.tell()
    toc = {'id': toc_id, 'offset': offset, 'bytes': length}
    regions = [*sections, toc]
    for item in regions:
        start, length = item['offset'], item['bytes']
        if length <= 0 or start < header_end or start + length > size:
            raise InvalidContainer('Section or TOC outside the input payload bounds')
    ordered = sorted(regions, key=lambda item: item['offset'])
    for left, right in zip(ordered, ordered[1:]):
        if left['offset'] + left['bytes'] > right['offset']:
            raise InvalidContainer('Overlapping sections or TOC')
    for item in regions:
        stream.seek(item['offset'])
        prefix = read_exact(stream, min(16, item['bytes']))
        item['prefix_hex'] = prefix.hex()
    toc['openssl_salted_marker'] = bytes.fromhex(toc['prefix_hex']).startswith(b'Salted__')
    stream.seek(0)
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return {
        'format': 'MSDU10', 'bytes': size, 'sha256': digest.hexdigest(),
        'declared_model_family': name.decode('ascii'), 'section_count': count,
        'sections': sections, 'toc': toc,
        'assessment': {
            'decrypted': False, 'signature_verified': False,
            'boot_compatibility': 'not_established', 'installation_supported': False,
            'interpretation': 'Container layout only; no conclusion about signing enforcement or flashability.'
        }
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--expect-family', help='Require this declared header family; not a device compatibility check')
    args = parser.parse_args(argv)
    try:
        with args.input.open('rb') as stream:
            result = inspect_stream(stream)
        if args.expect_family and result['declared_model_family'] != args.expect_family:
            raise InvalidContainer('Declared model family does not match --expect-family')
    except (OSError, InvalidContainer) as error:
        print('Inspection failed: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
