"""Reconstruct the current Thomas pickup repair; stage one bounded ROM."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import stage_excitebike_powerup_1110 as Ex
import check_thomas_powerup_progression_1110 as Fix
from nightly_patch_guard_v1 import check

R, NIGHTLY = Ex.R, Ex.NIGHTLY
PARENT = Ex.PIN
PIN = '6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d'


def reconstruct():
    parent, _ = Ex.reconstruct()
    assert sha256(parent).hexdigest() == PARENT
    image, kernel, cookie, record = Fix.proposal(parent)
    assert sha256(image).hexdigest() == PIN and len(image) == 2_097_168
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
    candidate = out/'candidate.nes'
    candidate.write_bytes(image)
    assert candidate.read_bytes() == image
    print(json.dumps(dict(passed=True, native_pending=True, ROM_written=True,
        output_files=1, output_bytes=len(image), ROM_SHA256=PIN,
        parent_ROM_SHA256=PARENT, source_record=record), sort_keys=True))


if __name__ == '__main__':
    main()
