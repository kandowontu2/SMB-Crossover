"""Stage one source-reconstructed WWF native pickup/armor candidate."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import stage_thomas_powerup_1110 as Thomas
import check_wwf_native_powerups_1110 as Fix
from nightly_patch_guard_v1 import check

R, NIGHTLY = Thomas.R, Thomas.NIGHTLY
PARENT = Thomas.PIN
PIN = '62c9a3d212659c1447afcb561113fa4ce1c2703fe6cd6be357a8b97ba20deb3c'


def reconstruct():
    parent, _ = Thomas.reconstruct()
    assert sha256(parent).hexdigest() == PARENT
    image, record = Fix.proposal(parent)
    assert sha256(image).hexdigest() == PIN and len(image) == 2_097_168
    assert len(record['patches']) == 5
    return image, record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    image, record = reconstruct()
    out.mkdir()
    target = out/'candidate.nes'
    target.write_bytes(image)
    assert target.read_bytes() == image
    print(json.dumps(dict(passed=True, native_pending=True, ROM_written=True,
        output_files=1, output_bytes=len(image), ROM_SHA256=PIN,
        parent_ROM_SHA256=PARENT, source_record=record), sort_keys=True))


if __name__ == '__main__':
    main()
