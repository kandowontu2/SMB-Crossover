"""Install the replayed Sonic injury fix and refresh the sole Current IPS."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_injury_prince_rebase_1110 as Fix
import deliver_prince_sonic_transport_1110 as Previous
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

Stage = Fix.Prince
SCRIPT = Stage.R/'tools/playthroughs/sonic_earned_injury_stdout_1110_v2.lua'
SCRIPT_PIN = 'a6e1dc5caf708a6d7fbe21bc7d7d18207061befc5e9bb1972bedb2e7125b182c'
OLD_RECEIPT = '00ac3ee5ae97f7eeed76aa2add63cdacfeda217d8f53fe5dd4b8873b39188f50'
SONIC_RECEIPT = 'b27c49992aa49955eec69819c3b6d1fc2f53cad6754b7ff6ba24fa1e28c7798d'
PRINCE_RECEIPT = '800fd9ee54cb740e1d065ecf777dd4ca6cf5cb7497f6a5261e55d268977c9572'
PATCH_PIN = '3981798af56cbd37efcd3283bfdd9e2bf339340476de553e7e99df86eabdb2af'
PREVIOUS_PATCH = '92527edf832ecb5349c3c3bfc568914a7fae3e746c5dc9982886b296ea9821cb'
REPORT = Stage.R/'docs/qa/sonic-earned-injury-delivery-1110.md'


def install(output):
    assert output.is_relative_to(Stage.R/'build') and output != Stage.R/'build'
    assert not output.exists()
    image, _, _, _ = Fix.reconstruct()
    assert image == Fix.CANDIDATE.read_bytes()
    before = check(Stage.NIGHTLY)
    old = Stage.NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == before['ROM_sha256'] == Stage.PIN
    ips = Previous.ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert Previous.apply_ips(Previous.SOURCE_BASE.read_bytes(), ips)[0] == image
    runs = (
        ('Sonic', SCRIPT, SCRIPT_PIN, 0, SONIC_RECEIPT),
        ('Prince', Previous.PRINCE, Previous.PRINCE_PIN, 3, PRINCE_RECEIPT),
    )
    try:
        Stage.NIGHTLY.write_bytes(image)
        assert Stage.NIGHTLY.read_bytes() == image
        assert check(Stage.NIGHTLY)['ROM_sha256'] == Fix.PIN
        for name, script, script_pin, variant, expected in runs:
            assert sha256(script.read_bytes()).hexdigest() == script_pin
            result = run(script, Stage.NIGHTLY, output/name, Fix.PIN, 180, variant)
            print(json.dumps(dict(event=name, passed=result['passed'],
                receipt_SHA256=result['receipt_SHA256'], reason=result['receipt']['reason'],
                outputs_written=result['outputs_written']), sort_keys=True), flush=True)
            assert result['passed'] and result['receipt_SHA256'] == expected
        after = check(Stage.NIGHTLY)
        assert Stage.NIGHTLY.read_bytes() == image and after['ROM_sha256'] == Fix.PIN
    except BaseException:
        Stage.NIGHTLY.write_bytes(old)
        assert Stage.NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, directly_installed=True, ROM_SHA256=Fix.PIN,
        previous_ROM_SHA256=Stage.PIN, IPS_SHA256=PATCH_PIN, IPS_bytes=len(ips),
        candidate_and_Downloads_receipts=[SONIC_RECEIPT, PRINCE_RECEIPT],
        guard_before=before, guard_after=after, output_files=0, backup_files=0),
        sort_keys=True), flush=True)


class Recipe:
    V1 = Stage.Transport.Stage.WWF.Previous.Thomas.Ex.Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base == Recipe.V1.BASE.read_bytes()
        return Fix.reconstruct()


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {Fix.PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Sonic now returns to the correct tier after a powered hit. Mesen verified an earned mushroom, '
        'the growth sequence, Goomba contact, and resumed movement on the installed ROM. '
        'Sonic is three Select presses from Mr. Gimmick. Original ring progression is still in development.\n\n'
        'Prince of Persia is one Select press from Excitebike. Mesen repeated his original jump and climb '
        'over four pipes and two gaps with both lives. All 100 names remain available. '
        'See docs/qa/sonic-earned-injury-delivery-1110.md for verification.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as base

    assert OLD_RECEIPT.encode() in REPORT.read_bytes()
    with patch.object(base, 'PIN', Fix.PIN), patch.object(base, 'PATCH_PIN', PATCH_PIN), \
         patch.object(base, 'OLD_PATCH', PREVIOUS_PATCH), \
         patch.object(base, 'RECEIPTS', (SONIC_RECEIPT, PRINCE_RECEIPT)), \
         patch.object(base, 'Fix', Recipe), patch.object(base, 'CANDIDATE', Fix.CANDIDATE), \
         patch.object(base, 'SCRIPT', SCRIPT), patch.object(base, 'SCRIPT_PIN', SCRIPT_PIN), \
         patch.object(base, 'REPORT', REPORT), patch.object(base, 'release_body', release_notes):
        base.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--output', type=Path, help='Install and replay from Downloads')
    command.add_argument('--report-sha', help='Publish after installation and source push')
    args = parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
