"""Preserve the actual Quick loader PASS and root-found black-sky failure."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha
from checkpoint_host_cadence_1030_v4 import archive_members


def main():
    out = R/'build/quickman-wram-host-cpu-v5'
    packet = out/'handoff.json'
    assert sha(packet) == '6d54978656a024a93b41e46bd3bba3c2c5f38ea2c6380f7d6a45c4f1c25f8c77'
    h = json.loads(packet.read_text())
    assert h['ROM_sha256'] == sha(out/'candidate.nes') == 'eed0ac40e6cffbf8877f504dfde2cc5c04c85f10038192a7d16d5c3bb24dfeaa'
    bindings = dict(h['bindings'])
    archive_members(out/'source-closure.zip', sha(out/'source-closure.zip'), bindings)
    for name, expected_exit in [('quickman-wram-native-v1', 1), ('quickman-wram-native-v2', 0)]:
        native = R/'build'/name
        budget = json.loads((native/'capture-budget.json').read_text())
        assert budget['returncode'] == expected_exit and not budget['violations']
        for path in native.iterdir():
            if path.is_file():
                bindings[str(path)] = sha(path)
    guard = R/'build/quickman-wram-native-guard-v2'
    for path in guard.iterdir():
        if path.is_file():
            bindings[str(path)] = sha(path)
    result = json.loads((R/'build/quickman-wram-native-v2/result.json').read_text())
    assert result['passed'] and result['code8192_data8192_exact'] and result['loader_reads'] == 18450
    assert result['jump'] and result['fan'] and result['scroll']
    for path in [packet, Path(__file__).resolve(), R/'tools/audit/checkpoint_host_cadence_1030_v4.py']:
        bindings[str(path)] = sha(path)
    save('quickman-banked-host-native-visual-negative', dict(
        status='ACTUAL_LOADER_AND_CONTROLLER_SMOKE_PASS_ROOT_VISUAL_FAIL_NO_INSTALL',
        ROM_sha256=h['ROM_sha256'], private_WRAM_bytes=32768,
        retained_PRG_lease=10060, PRG_used=1895, code_bytes=6491, data_bytes=1921,
        stream_CHR_pages=[884, 893], existing_body_CHR_pages=[251, 256],
        source_CPU_receipt_groups=11, frozen_source_bindings=len(h['bindings']), native=result,
        root_visual_review='Viewed actual cold menu, jump/fan and gameplay-final PNGs. Quick body/weapon visible, but the normal1-1 sky is BLACK. This is a graphical regression and invalidates overall visual/admission claims.',
        first_fixture_negative='Original write guard rejected legal global-boot cookie invalidation before menu. Narrow successor authenticates exact STA and consumes oneDFE0=0 token; all other active payload writes remain forbidden.',
        actual_boot_write='Native sourcePC A70:A939/callbackPC A93C, DFE0=0, rawA C6/rawC2, selected0/mode0/menu0/alt0 atframe4 matches genuine QwBoot.',
        limits=['Black overworld sky must be traced to its real producer and repaired before shared installation.',
                'Reported maxMain661853 includes cold loader and cannot establish gameplay cadence.',
                'No native1-1/full-powerup/two-player/warm-loader/source-audio or60Hz admission.']), bindings)


if __name__ == '__main__':
    main()
