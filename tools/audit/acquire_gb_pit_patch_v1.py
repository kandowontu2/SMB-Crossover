"""Recover only the user-linked Pit graphics patch, with a 24 MB transfer cap.

No game ROM is downloaded, patched or redistributed. The historical patch's
required base digest differs from local ROMs; acquisition is not compatibility.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import zipfile

from inspect_rhdn_patch_archive_v2 import RemoteZip, URL, SIZE, OUT

PREFIX = 'hacks/NES/Kid Icarus/Kid Icarus - Retold/'
MEMBERS = {
    'scraped_info.txt': 'dad100eea0e4437057d22cee70fbb11b753e3aeb2775343b7668f796e044f1a4',
    'og_readme.txt': '385b4bc27b78160c286f571068869141c5ec89b708484d7d1b9483ae04b10a6a',
    'KidIcarus-Retold-Final.zip': '30ccbe8c3a9bd763d0a4865262e22b9009e5ca26613886a4e200c23e6a6a3f8b',
    'Kid Icarus - Retold_screenshot0.jpg': '9152020f3456899defaf8f027eb2808a8bbacc55237063ee4338ae39096fad4c',
}
PATCH_SHA = '81c34ed0e92994229b5d81b435deddd4c463c9ae35e5c76cdaef5a1fa250445d'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--verify-existing', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if args.verify_existing:
        content = {name: (output / name).read_bytes() for name in MEMBERS}
    else:
        assert not output.exists(), 'Use a fresh destination; retain prior evidence'
        with RemoteZip() as remote, zipfile.ZipFile(remote) as archive:
            content = {}
            for name, expected in MEMBERS.items():
                info = archive.getinfo(PREFIX + name)
                assert info.file_size <= 100_000 and not info.is_dir()
                data = archive.read(info)
                assert digest(data) == expected, name
                content[name] = data
            receipt = dict(archive_url=URL, archive_bytes=SIZE,
                           bulk_archive_downloaded=False,
                           transferred_bytes=remote.transferred,
                           exact_range_reads=remote.requests)
    for name, expected in MEMBERS.items():
        assert digest(content[name]) == expected, name
    assert 'http://www.romhacking.net/hacks/1459/' in content['scraped_info.txt'].decode()
    with zipfile.ZipFile(io.BytesIO(content['KidIcarus-Retold-Final.zip'])) as patch_zip:
        info = patch_zip.getinfo('KidIcarus-Retold-Final/Kid Icarus [ReTold].ips')
        assert info.file_size == 17095
        patch = patch_zip.read(info)
    assert digest(patch) == PATCH_SHA and patch.startswith(b'PATCH')
    if args.verify_existing:
        assert (output / 'retold.ips').read_bytes() == patch
    else:
        output.mkdir(parents=True)
        for name, data in content.items():
            (output / name).write_bytes(data)
        (output / 'retold.ips').write_bytes(patch)
        receipt['files'] = {name: digest(data) for name, data in content.items()}
        receipt['patch_sha256'] = PATCH_SHA
        receipt['base_compatibility'] = 'UNPROVEN; original author base differs from local ROMs'
        (output / 'bounded-acquisition.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(verified=True, patch_sha256=PATCH_SHA,
                         downloaded=not args.verify_existing, ROM_modified=False)))


if __name__ == '__main__':
    main()
