"""Inspect a remote patch ZIP with strict HTTP-range and transfer limits.

Never download the multi-gigabyte archive or extract a directory tree. This
only lists matching member metadata; individual patch acquisition is separate.
The authenticated ZIP64 directory is13,026,873B, so v2 raises only the single
read ceiling to16MB; the unchanged total transfer cap remains24MB.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/source-acquisition/kid-icarus-retold-2026-10-29'
URL = 'https://archive.org/download/rhdn-20210119/RHDN_20210119.zip'
SIZE = 5_794_342_133


class RemoteZip(io.RawIOBase):
    def __init__(self):
        super().__init__()
        self.position = self.transferred = 0
        self.requests = []
        self.etag = None

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        base = 0 if whence == 0 else self.position if whence == 1 else SIZE
        assert whence in (0, 1, 2)
        self.position = base + offset
        assert 0 <= self.position <= SIZE
        return self.position

    def read(self, size=-1):
        if size < 0:
            size = SIZE - self.position
        size = min(size, SIZE - self.position)
        if not size:
            return b''
        assert size <= 16_000_000 and self.transferred + size <= 24_000_000
        start, end = self.position, self.position + size - 1
        request = urllib.request.Request(URL, headers={
            'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity',
            'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=20) as response:
            assert response.status == 206, 'Server ignored Range; refuse bulk download'
            assert response.headers['Content-Range'] == f'bytes {start}-{end}/{SIZE}'
            etag = response.headers.get('ETag')
            if self.requests:
                assert etag == self.etag, 'Archive identity changed between ranges'
            self.etag = etag
            data = response.read(size + 1)
            assert len(data) == size
            self.requests.append(dict(start=start, end=end, bytes=size,
                final_url=response.url, etag=etag,
                sha256=hashlib.sha256(data).hexdigest()))
        self.position += size
        self.transferred += size
        return data


def main():
    target = OUT / 'remote-archive-index-v2.json'
    assert not target.exists(), 'Preserve the first bounded inspection'
    OUT.mkdir(parents=True, exist_ok=True)
    with RemoteZip() as remote, zipfile.ZipFile(remote) as archive:
        matches = [dict(name=q.filename, bytes=q.file_size,
                    compressed=q.compress_size, CRC32=f'{q.CRC:08x}')
                   for q in archive.infolist()
                   if re.search(r'(^|/)1459(?:/|\D|$)|kid.?icarus.*retold', q.filename, re.I)]
        report = dict(status='REMOTE_CENTRAL_DIRECTORY_INSPECTED_ONLY',
            archive_url=URL, archive_bytes=SIZE, members=len(archive.infolist()),
            matches=matches, transferred_bytes=remote.transferred,
            exact_range_reads=remote.requests, extracted_files=0,
            bulk_archive_downloaded=False)
        target.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
