"""Replace Downloads directly, repeat the earned pickup, retain no backup."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from deliver_manual_title_1110 import ips_for, apply_ips, SOURCE_BASE
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
from stage_excitebike_powerup_1110 import R, NIGHTLY, PARENT, PIN, reconstruct

CANDIDATE = R/'build/excitebike-powerup-native-1110/candidate.nes'
SCRIPT = R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110_v4.lua'
SCRIPT_PIN = '547675a20cda944233757c664a89fde1a97d98435d98ce5e09be43b5c663b228'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    image, record = reconstruct()
    assert CANDIDATE.read_bytes() == image
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    before = check(NIGHTLY)
    old = NIGHTLY.read_bytes()
    assert before['ROM_sha256'] == sha256(old).hexdigest() == PARENT
    patch = ips_for(image)
    assert apply_ips(SOURCE_BASE.read_bytes(), patch)[0] == image
    NIGHTLY.write_bytes(image)
    try:
        assert NIGHTLY.read_bytes() == image
        assert check(NIGHTLY)['ROM_sha256'] == PIN
        result = run(SCRIPT, NIGHTLY, out, PIN, 150)
        assert result['passed'] and result['receipt']['powerup_ticks'] == 60
        assert result['receipt']['terminal']['x'] == 306
        assert result['receipt']['terminal']['lives'] == 2
        assert NIGHTLY.read_bytes() == CANDIDATE.read_bytes() == image
        after = check(NIGHTLY)
        assert after['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)  # rollback bytes held only in memory
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, directly_installed=True, backup_files=0,
        generated_files=0, ROM_SHA256=PIN, previous_ROM_SHA256=PARENT,
        IPS_SHA256=sha256(patch).hexdigest(), IPS_bytes=len(patch),
        patch_reconstruction_equals_tested_Downloads=True,
        candidate_equals_tested_Downloads=True, source_record=record,
        guard_before=before, guard_after=after, native=result), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
