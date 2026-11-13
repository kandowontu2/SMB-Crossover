"""Install only the exact physically qualified Bub/Bob incremental nightly."""
from hashlib import sha256
import json
from pathlib import Path

from nightly_patch_guard_v1 import check

R = Path(__file__).resolve().parents[2]
SOURCE = R / 'build/bub-empty-native-1113/candidate.nes'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PARENT = '7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
TESTED = 'f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
RECEIPTS = {
    'Bub_full': '28112772dcdc8228fb607b02112ce8ff914e74f5b3a80ed8893f600da05c6780',
    'Bob_full': '5270b7fbb1d16f03f7cb520679ca65a25afe21e57d954ca953f3951d6359529a',
    'Bub_mushroom': '020e61bc3075486dfdf9d40439bf92e2ce9c3b8a2d406cfb9e5cea11050e7086',
    'Bob_mushroom': '0e93e4c85176b5f9d39714156e547b36cc76be93b3f163ef5c2e149ccdbc786c',
}


def main():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    image = SOURCE.read_bytes()
    assert len(image) == 2_097_168 and sha256(image).hexdigest() == TESTED
    # Direct replacement is explicitly requested; no temporary or backup ROM.
    assert NIGHTLY.write_bytes(image) == len(image)
    assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == TESTED
    print(json.dumps(dict(installed=True, path=str(NIGHTLY), ROM_SHA256=TESTED,
        tested_candidate_byte_identical=True, previous_SHA256=PARENT,
        native_receipts=RECEIPTS, backups_created=0, patches_created=0,
        releases_created=0, post_install_launch_still_required=True)), flush=True)


if __name__ == '__main__':
    main()
