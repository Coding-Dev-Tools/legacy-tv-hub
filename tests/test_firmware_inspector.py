import importlib.util
import io
import contextlib
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('firmware_inspector', ROOT/'tools/inspect_firmware.py')
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def fixture():
    # The documented 32-bit MSDU10 layout; includes a TOC, two data regions and closing zero.
    family = b'T-TESTFAMILY'
    header_end = 10 + 2 * 12 + 16 + 1 + len(family) + 4
    toc = b'Salted__' + b'12345678' + b'A' * 16
    first = b'B' * 32
    second = b'C' * 16
    data = b'MSDU10' + struct.pack('<I', 2)
    data += struct.pack('<III', 1, header_end + len(toc), len(first))
    data += struct.pack('<III', 2, header_end + len(toc) + len(first), len(second))
    data += struct.pack('<IIII', 0, 1, header_end, len(toc))
    data += bytes([len(family)]) + family + b'\0' * 4
    return bytearray(data + toc + first + second + b'\0' * 4)


class FirmwareInspectorTests(unittest.TestCase):
    def inspect(self, data):
        return inspector.inspect_stream(io.BytesIO(data))

    def test_valid_layout_and_read_only_interpretation(self):
        data = fixture()
        result = self.inspect(data)
        self.assertEqual(result['declared_model_family'], 'T-TESTFAMILY')
        self.assertEqual(result['section_count'], 2)
        self.assertTrue(result['toc']['openssl_salted_marker'])
        self.assertFalse(result['assessment']['signature_verified'])
        self.assertFalse(result['assessment']['installation_supported'])
        self.assertEqual(result['assessment']['boot_compatibility'], 'not_established')
        self.assertEqual(data, fixture())

    def test_truncated_headers(self):
        for length in (0, 5, 9, 17, 49, 55):
            with self.subTest(length=length), self.assertRaises(inspector.InvalidContainer):
                self.inspect(fixture()[:length])

    def test_other_format_is_rejected(self):
        data = fixture(); data[:6] = b'MSDU11'
        with self.assertRaises(inspector.InvalidContainer): self.inspect(data)

    def test_outside_file_and_header_ranges(self):
        for offset, length in ((0, 1), (0xffffffff, 32), (65, 0), (100, 0xffffffff)):
            data = fixture(); struct.pack_into('<II', data, 14, offset, length)
            with self.subTest(offset=offset, length=length), self.assertRaises(inspector.InvalidContainer):
                self.inspect(data)

    def test_overlapping_regions(self):
        data = fixture()
        first_offset, = struct.unpack_from('<I', data, 14)
        struct.pack_into('<I', data, 26, first_offset + 1)
        with self.assertRaises(inspector.InvalidContainer): self.inspect(data)

    def test_duplicate_ids(self):
        data = fixture(); struct.pack_into('<I', data, 22, 1)
        with self.assertRaises(inspector.InvalidContainer): self.inspect(data)

    def test_excessive_count(self):
        data = fixture(); struct.pack_into('<I', data, 6, 0xffffffff)
        with self.assertRaises(inspector.InvalidContainer): self.inspect(data)

    def test_unprintable_family(self):
        data = fixture(); data[51] = 10
        with self.assertRaises(inspector.InvalidContainer): self.inspect(data)

    def test_cli_rejects_wrong_family_without_changing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = Path(directory)/'upgrade.msd'
            payload.write_bytes(fixture())
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = inspector.main([str(payload), '--expect-family', 'T-OTHER'])
            self.assertEqual(result, 2)
            self.assertEqual(stdout.getvalue(), '')
            self.assertIn('does not match', stderr.getvalue())
            self.assertEqual(payload.read_bytes(), fixture())


if __name__ == '__main__':
    unittest.main()
