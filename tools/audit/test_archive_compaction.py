from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import pack_generated_archive as packer
from capture_budget import WORKSPACE


class VerifiedPacking(unittest.TestCase):
    def setUp(self):
        parent = WORKSPACE/'build'
        self.temp = tempfile.TemporaryDirectory(prefix='archive-pack-check-', dir=parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(parent.resolve())
        self.addCleanup(self.temp.cleanup)
        self.group = self.root/'2026-10-24-test'
        self.group.mkdir()
        self.packed = self.root/'packed'
        for name, value in [('ARCHIVE', self.root), ('PACKED', self.packed),
                            ('KEEP', ('2026-10-24-test/active',))]:
            setter = patch.object(packer, name, value)
            setter.start()
            self.addCleanup(setter.stop)
        (self.group/'active').mkdir()
        (self.group/'active/live.txt').write_text('active input')
        (self.group/'video.mp4').write_bytes(b'video')
        (self.group/'original.nes').write_bytes(b'rom')
        self.data = self.group/'old-data.bin'
        self.data.write_bytes(bytes(range(256))*16)

    def test_exact_recoverable_bytes_and_kept_inputs(self):
        expected = self.data.read_bytes()
        result = packer.pack(self.group)
        self.assertEqual(result['removed_files'], 1)
        self.assertFalse(self.data.exists())
        for name in ['active/live.txt', 'video.mp4', 'original.nes']:
            self.assertTrue((self.group/name).exists())
        with zipfile.ZipFile(result['archive']) as archive:
            member = archive.infolist()[0]
            self.assertEqual(archive.read(member), expected)
            self.assertEqual(json.loads(member.comment)['bytes'], len(expected))
        with self.assertRaises(AssertionError):
            packer.pack(self.group)

    def test_failed_verification_preserves_source(self):
        with patch.object(packer, 'sha_stream', return_value='invalid'):
            with self.assertRaises(AssertionError):
                packer.pack(self.group)
        self.assertTrue(self.data.exists())
        self.assertFalse((self.packed/(self.group.name+'.zip')).exists())

    def test_output_limit_preserves_source(self):
        with patch.object(packer, 'ZIP_CAP', 16):
            with self.assertRaises(RuntimeError):
                packer.pack(self.group)
        self.assertTrue(self.data.exists())


if __name__ == '__main__':
    unittest.main()
