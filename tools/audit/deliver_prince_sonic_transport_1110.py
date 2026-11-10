"""Repeat Prince's crossing and Sonic's stage clear on the installed ROM."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
import stage_prince_sonic_transport_1110 as Stage

PRINCE = Stage.R/'tools/playthroughs/prince_original_first_pipe_stdout_1110.lua'
PRINCE_PIN = 'e9b45ae96c00ee55b456200f346ab2e4f22c78013a0820e98910ecddcc6dc65e'
SONIC = Stage.R/'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
SONIC_PIN = '2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee'
CANDIDATE = Stage.R/'build/prince-sonic-transport-native-1110/candidate.nes'


def verify(path, output):
    receipts = {}
    for name, script, script_pin, variant in (
        ('Prince', PRINCE, PRINCE_PIN, 3), ('Sonic', SONIC, SONIC_PIN, 0),
    ):
        assert sha256(script.read_bytes()).hexdigest() == script_pin
        result = run(script, path, output/name, Stage.PIN, 180, variant)
        receipt = result['receipt']
        print(json.dumps(dict(event=name, passed=result['passed'], receipt=receipt,
            receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
            actual_Mesen=True, output_files=result['outputs_written']), sort_keys=True), flush=True)
        assert result['passed']
        if name == 'Prince':
            fourth = receipt['later_route']['fourth_full_cap']
            assert (fourth['x'], fourth['y'], fourth['action']) == (928, 112, 42)
            assert receipt['later_route']['first_gap']['x'] == 1175
            assert receipt['later_route']['second_gap']['x'] == 1461
            assert (receipt['terminal']['x'], receipt['terminal']['hp'], receipt['terminal']['lives']) == (1461, 4, 2)
            assert len(receipt['later_caps']) == 2 and len(receipt['fourth_support_publications']) == 5
            assert not receipt['added_helpers']
        else:
            assert receipt['native_flag'] and receipt['native_castle'] and receipt['active_1_2']
            assert receipt['terminal']['lives'] == 2 and receipt['terminal']['level'] == 1
            assert receipt['calls']['OriginalSonicFrame'] == 1423 and len(receipt['jump_events']) == 17
        receipts[name] = result['receipt_SHA256']
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prince-receipt', required=True)
    parser.add_argument('--sonic-receipt', required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Stage.R/'build') and output != Stage.R/'build' and not output.exists()
    expected = {'Prince': args.prince_receipt, 'Sonic': args.sonic_receipt}
    assert all(len(value) == 64 for value in expected.values())
    image, _ = Stage.reconstruct()
    assert image == CANDIDATE.read_bytes()
    before = check(Stage.NIGHTLY)
    old = Stage.NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == before['ROM_sha256'] == Stage.PARENT
    patch = ips_for(image)
    assert apply_ips(SOURCE_BASE.read_bytes(), patch)[0] == image
    Stage.NIGHTLY.write_bytes(image)
    try:
        assert Stage.NIGHTLY.read_bytes() == image and check(Stage.NIGHTLY)['ROM_sha256'] == Stage.PIN
        assert verify(Stage.NIGHTLY, output) == expected
        assert Stage.NIGHTLY.read_bytes() == CANDIDATE.read_bytes() == image
        after = check(Stage.NIGHTLY)
        assert after['ROM_sha256'] == Stage.PIN
    except BaseException:
        Stage.NIGHTLY.write_bytes(old)
        assert Stage.NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, directly_installed=True, ROM_SHA256=Stage.PIN,
        previous_ROM_SHA256=Stage.PARENT, IPS_SHA256=sha256(patch).hexdigest(), IPS_bytes=len(patch),
        matching_candidate_receipts=expected, guard_before=before, guard_after=after,
        patch_reconstructs_tested_Downloads=True, output_files=0, backup_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
