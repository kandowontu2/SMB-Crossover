"""Deliver the final startable-roster composition with bounded native receipts."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import prepare_manual_dual_native_1110 as P
from deliver_giant_impact_1110 import packet_result, NIGHTLY, SMALL
from deliver_manual_right_1110 import motion
from deliver_manual_title_1110 import ips_for, ASSET, REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import prepare, sha, R
from stage_complete_roster_1110 import apply, BASE, BASE_PIN

NATIVE = R / 'build/complete-roster-native-1110'
ROM = NATIVE / 'candidate.nes'
PROOF = NATIVE / 'combined-proof.json'
INVENTORY = R / 'build/complete-roster-inventory-1110/inventory.json'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
PROOF_PIN = '448bf27874fe4f5a1268dc087aaacb635111d25811a4f63b00e17fe8c2480449'


def evidence():
    q = json.loads(PROOF.read_text())
    assert sha(PROOF) == PROOF_PIN and q['passed'] and q['source_ready']
    assert q['ROM_SHA256'] == sha(ROM) == PIN and q['strict_disjoint']
    assert q['parent_SHA256'] == sha(BASE) == BASE_PIN
    for name, digest in q['bindings'].items():
        assert sha(R / name) == digest, name
    raw = apply(BASE.read_bytes(), q['patches'], 'Final delivery')
    assert len(q['patches']) == 50 and raw == ROM.read_bytes()
    names = [f'22-{i}' for i in range(4)] + [f'29-{i}' for i in range(6)]
    results = {}
    for name in names + ['prince', 'dkjr', 'sonic', 'jay', 'steve',
                         'regression/mini', 'regression/getsu']:
        packet = NATIVE / 'packets' / name
        result = packet_result(packet, ROM, PIN)
        if name == 'regression/mini':
            assert result['full_stage'] and result['terminal_native']['NumberofLives'] == 2
            assert result['terminal_native']['LevelNumber'] == 1
        else:
            assert result['terminal']['lives'] == 2, name
        if name in names:
            motion(result)
        results[name] = sha(packet / 'capture/result.json')
    assert len(results) == 17
    cadence = json.loads((NATIVE / 'packets/regression/mini/capture/timing.json').read_text())['cadence']['fullstage']
    assert cadence['physical'] == cadence['updates'] == 3494
    assert all(cadence.get(k, 0) == 0 for k in ('lag_nmi', 'zero_update', 'no_controller_read'))
    inventory = json.loads(INVENTORY.read_text())
    assert inventory['passed'] and inventory['ROM_sha256'] == PIN
    assert inventory['distinct_named_entries'] == inventory['confirmable_named_entries'] == 100
    assert inventory['locked'] == []
    assert all(v['status'] == 'startable' for v in inventory['requested'].values())
    return raw, cadence, results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('deliver', 'publish'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build'
    raw, cadence, results = evidence()
    receipt = out / 'verified-delivery.json'
    patch = out / ASSET
    if args.action == 'deliver':
        assert not out.exists()
        before = check(NIGHTLY)
        assert before['ROM_sha256'] == BASE_PIN
        out.mkdir()
        try:
            NIGHTLY.write_bytes(raw)
            assert check(NIGHTLY)['ROM_sha256'] == PIN
            symbols = (P.Old.SYMBOL_BASE.with_suffix('.lbl'), P.Old.SYMBOL_BASE.with_suffix('.dbg'))
            for name in ('sonic', '22-0'):
                old = NATIVE / 'packets' / name
                packet = out / name
                prepare(packet, NIGHTLY, (old / 'controller.lua').read_text(),
                        {Path(__file__), PROOF, INVENTORY, old / 'controller.lua', old / 'capture/result.json'},
                        expected=PIN, timeout=180, allow_interactive=True, rom_symbols=symbols,
                        scope='Actual Downloads launch context: exact final-hash controller-only Sonic opening or Fighter V/H helper replay. Other fifteen native cases bind byte-identical candidate.')
                subprocess.run([sys.executable, '-B', str(SMALL), '--files', '10', str(packet / 'run.py')], check=True)
                result = packet_result(packet, NIGHTLY, PIN)
                assert result['terminal']['lives'] == 2
                if name == '22-0':
                    motion(result)
            patch.write_bytes(ips_for(raw))
            q = dict(installed=True, Downloads_launch_verified=True, backup_created=False,
                     ROM_SHA256=PIN, previous_ROM_SHA256=BASE_PIN, IPS_SHA256=sha(patch), IPS_roundtrip=True,
                     proof_SHA256=sha(PROOF), inventory_SHA256=sha(INVENTORY), script_SHA256=sha(Path(__file__)),
                     distinct_named_entries=100, confirmable_named_entries=100, locked=[],
                     native_results=results, mini_cadence=cadence,
                     Downloads_results={n: sha(out / n / 'capture/result.json') for n in ('sonic', '22-0')},
                     before=before, after=check(NIGHTLY),
                     scope='100 named menu entries CPU-confirmable; 17 final-hash native cases passed. Actual Downloads Sonic and Fighter helper repeat passed. Startup prototypes are not full-route/donor-ability qualification.',
                     limitations=['Sonic borrows native Mario physics, abilities and audio.',
                                  'Jay and Steve borrow Mike movement, weapons, health and audio; level-select cheats clear their prototype choice.',
                                  'Prince later Easy landing and DKJr first-pipe lift/jump detach remain unqualified.',
                                  'Existing Mini preview header corruption is inherited when cycling to Sonic.'])
            receipt.write_text(json.dumps(q, indent=2) + '\n')
        except (Exception, KeyboardInterrupt):
            NIGHTLY.write_bytes(BASE.read_bytes())
            assert check(NIGHTLY)['ROM_sha256'] == BASE_PIN
            raise
    else:
        q = json.loads(receipt.read_text())
        assert q['ROM_SHA256'] == check(NIGHTLY)['ROM_sha256'] == PIN
        assert q['proof_SHA256'] == sha(PROOF) and q['inventory_SHA256'] == sha(INVENTORY)
        assert q['script_SHA256'] == sha(Path(__file__))
        assert q['IPS_SHA256'] == sha(patch) and patch.read_bytes() == ips_for(raw)
        for name in ('sonic', '22-0'):
            packet_result(out / name, NIGHTLY, PIN)
        current = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases/tags/Current'], encoding='utf-8'))
        old, = current['assets']
        assert old['name'] == ASSET
        notes = out / 'release-notes.txt'
        notes.write_text('Current MMC5 WIP. Apply to clean headered Super Mario Bros. (World).\n\n'
                         'All 100 current named roster entries can start; no remaining menu locks. '
                         'Sonic: Select on Mario ten times. Jay McCray / Steve Hermann: Select on Mike Jones once / twice. '
                         'Prince: Select on Excitebike. DK Jr.: Select on Donkey Kong.\n'
                         'These are unfinished prototypes: Sonic currently borrows Mario movement/abilities/audio; '
                         'Jay/Steve borrow Mike movement/weapons/health/audio. Active level-select cheats clear Jay/Steve selection. '
                         'Prince later Easy landing and DKJr first-pipe lift/jump-detach remain unqualified. '
                         'Mini preview header corruption can persist when cycling to Sonic.\n'
                         'All six WWF wrestlers and four Final Fantasy classes now have independent Up+Select vertical and '
                         'Down+Select horizontal native helpers. Horizontal starts right, travels112px, returns and repeats. '
                         'Mini/Karnov retain both controls.\n'
                         '17 final-ROM native tests passed: ten helper variants, five new openings, Mini full1-1 and Getsu earned powerups. '
                         'Mini retains3494updates/3494gameplayframes, zero lag NMIs/missed updates. '
                         'Actual Downloads Sonic and Fighter tests repeat successfully. Broader full-roster stage/powerup review remains unfinished.\n'
                         'ROM SHA-256 ' + PIN + '\n')
        subprocess.run(['gh', 'release', 'upload', 'Current', str(patch), '--clobber', '--repo', REPO], check=True)
        subprocess.run(['gh', 'release', 'edit', 'Current', '--latest', '--notes-file', str(notes), '--repo', REPO], check=True)
        latest = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases/latest'], encoding='utf-8'))
        asset, = latest['assets']
        assert latest['tag_name'] == 'Current' and asset['name'] == ASSET and asset['digest'] == 'sha256:' + sha(patch)
        q.update(release_tag='Current', release_is_latest=True, sole_asset=ASSET, release_asset_digest=asset['digest'])
        receipt.write_text(json.dumps(q, indent=2) + '\n')
    print(args.action, PIN, flush=True)


if __name__ == '__main__':
    main()
