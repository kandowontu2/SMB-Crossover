"""Exact FF physical routes and optional Downloads delivery, zero capture files."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_ff_head_corner_1110_v2 as Fix
import run_stdout_mesen_1110 as M
from nightly_patch_guard_v1 import check
from deliver_manual_title_1110 import ips_for

R = Path(__file__).resolve().parents[2]
PIN = '96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'
PARENT = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
SCRIPT = R / 'tools/playthroughs/ff_full_stage_stdout_1110_v5.lua'
SCRIPT_PIN = 'aa18b8bcf1b81bbd817e507d1228a5f889dfea09cf73015c68f93de2c8fa4025'
CANDIDATE = R / 'build/ff-head-corner-native-1110/candidate.nes'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def compact(q):
    p = q['receipt']
    return dict(passed=q['passed'], ROM_SHA256=q['ROM_SHA256'],
        script_SHA256=q['script_SHA256'], emulator_SHA256=q['emulator_SHA256'],
        receipt_SHA256=q['receipt_SHA256'], seconds=q['seconds'],
        variant=p['variant'], class_name=p['class_name'], reason=p['reason'],
        terminal=p['terminal'], first_active_1_1=p.get('first_active_1_1'),
        native_flag=p.get('native_flag'), active_1_2=p.get('active_1_2'),
        earned_attack=p.get('earned_attack'), cadence=p['cadence'],
        camera_max=p['physics']['max_camera_step'],
        mushroom_ticks=p['mushroom']['ticks'], flower_ticks=p['flower']['ticks'],
        mushroom_palette=p['mushroom'].get('palette'), flower_palette=p['flower'].get('palette'),
        priority_edges=p['priority_edges'], calls=p['calls'],
        failure_jump_delivery_tail=p.get('jump_delivery', [])[-3:] if not q['passed'] else None,
        outputs_written=q['outputs_written'], shared_Mesen_queue=q['shared_Mesen_queue'],
        capture_watchdog=q['capture_watchdog'], other_processes_untouched=q['other_processes_untouched'],
        full_receipt_in_memory_only=True, compact_summary=True)


def qualify(q, variant):
    p = q['receipt']
    assert q['passed'] and q['returncode'] == 0
    assert q['script_SHA256'] == SCRIPT_PIN and q['ROM_SHA256'] == PIN
    assert p['variant'] == variant and p['full_1_1'] and p['native_flag']
    assert p['mushroom']['ticks'] == p['flower']['ticks'] == 60
    assert p['earned_attack'] and not p['script_RAM_writes'] and not p['save_load_or_cheats']
    s = p['active_1_2']
    assert (s['world'], s['level'], s['area_type'], s['engine'], s['task']) == (0, 1, 2, 8, 3)
    assert s['lives'] == 2 and s['power'] == s['earned'] == 2
    assert p['physics']['max_camera_step'] <= 3
    assert not q['outputs_written'] and not q['initial_output_files'] and not q['final_output_files']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--variants', type=int, nargs='+', choices=range(4), default=list(range(4)))
    ap.add_argument('--install', action='store_true')
    args = ap.parse_args()
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    image = CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    assert Fix.proposal(Fix.V1.BASE.read_bytes())[0] == image
    assert len(set(args.variants)) == len(args.variants)
    if args.install:
        assert sorted(args.variants) == list(range(4)), 'Delivery requires all four physical runs in this invocation'
    results = []
    for variant in args.variants:
        q = M.run(SCRIPT, CANDIDATE, args.output.resolve(), PIN, 180, variant)
        # Preserve an informative failure and stop. A failed controller never
        # installs a candidate or removes the previously delivered nightly.
        print(json.dumps(dict(event='candidate_native', result=compact(q))), flush=True)
        qualify(q, variant)
        results.append(compact(q))
    delivery = None
    if args.install:
        before = check(NIGHTLY)
        assert before['ROM_sha256'] == PARENT
        original_nightly = NIGHTLY.read_bytes()  # memory only, no backup file
        patch = ips_for(image)
        try:
            NIGHTLY.write_bytes(image)
            assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
            launched = M.run(SCRIPT, NIGHTLY, args.output.resolve(), PIN, 180, 0)
            print(json.dumps(dict(event='Downloads_native', result=compact(launched))), flush=True)
            qualify(launched, 0)
            after = check(NIGHTLY)
            assert after['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
            delivery = dict(installed=True, Downloads_launch_verified=True, backup_created=False,
                ROM_SHA256=PIN, previous_ROM_SHA256=PARENT, before=before, after=after,
                IPS_roundtrip=True, IPS_SHA256=sha256(patch).hexdigest(), IPS_bytes=len(patch),
                native=compact(launched), Current_release_refresh_pending=True)
        except BaseException:
            NIGHTLY.write_bytes(original_nightly)
            assert check(NIGHTLY)['ROM_sha256'] == PARENT
            raise
    print(json.dumps(dict(passed=True, native_Mesen=True, ROM_SHA256=PIN,
        output_files=0, results=results, delivery=delivery,
        scope='Earned mushroom/flower and actual attack, native non-shortcut1-1/flag/pipe to activeunderground1-2, noinjury. Not shortcut/everyenemy/allattacks/audibleoutput/exhaustivegraphics/originalsourceparity/lagfree.')), flush=True)


if __name__ == '__main__':
    main()
