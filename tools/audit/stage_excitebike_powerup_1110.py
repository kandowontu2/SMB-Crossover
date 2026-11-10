"""Stage one bounded, source-reconstructed Excitebike progression candidate."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_excitebike_powerup_progression_1110 as Fix
import check_ff_mux_unused_tail_1110 as Mux
from nightly_patch_guard_v1 import check

R = Path(__file__).resolve().parents[2]
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PARENT = 'a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
PIN = 'a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0'


def reconstruct():
    parent = Mux.proposal(Mux.Fix.V1.BASE.read_bytes())[0]
    assert sha256(parent).hexdigest() == PARENT
    image, kernel, cookie, record = Fix.proposal(parent)
    assert sha256(image).hexdigest() == PIN
    assert len(image) == 2_097_168 and record['changed_bytes'] == 34
    return image, record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    guard = check(NIGHTLY)
    assert guard['ROM_sha256'] == PARENT
    image, record = reconstruct()
    out.mkdir()
    candidate = out/'candidate.nes'
    candidate.write_bytes(image)
    assert candidate.read_bytes() == image
    print(json.dumps(dict(passed=True, ROM_written=True, native_pending=True,
        parent_ROM_SHA256=PARENT, ROM_SHA256=PIN, source_record=record,
        output_files=1, output_bytes=len(image), output=str(candidate)), sort_keys=True))


if __name__ == '__main__':
    main()
