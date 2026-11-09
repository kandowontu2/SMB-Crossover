"""Deliver the tested shared side-collision change to Downloads and Current."""

import argparse
import json
from pathlib import Path
import subprocess

from build_storage_guard_v1 import preflight
from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from deliver_shared_sparse_draw_1110 import ASSET, REPO, ROOT as PRIOR, installer
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import R, sha
from prepare_shared_gameplay_cadence_1110 import NIGHTLY, SPARSE, SPARSE_SHA


ROOT = R / 'build/shared-side-cadence-native-1110'
CPU = R / 'build/shared-side-tank-precheck-1110/proof.json'
PIN = 'ba3cba071547402fd81398d8b69659fa1b7d20cef9dfcda4df3fe8554ec592de'


def opening(packet, pin, owner, expected):
    ready, capture = packet / 'ready.json', packet / 'capture'
    bound, result = read(capture / 'binding.json'), read(capture / 'result.json')
    assert bound['ready_sha256'] == sha(ready) and bound['exit_code'] == 0
    assert bound['ROM_sha256'] == result['ROM_sha256'] == pin
    assert result['raw'] == owner and result['controller_only']
    phases = result['phases']
    assert [p['phase'] for p in phases] == ['idle', 'walk']
    assert tuple(p['no_controller_read'] for p in phases) == expected
    assert tuple(p['lag_nmi'] for p in phases) == expected
    assert [(p['updates'], p['contacts'], p['x_initial'], p['x_final']) for p in phases] == [
        (120, 0, 40, 40), (175, 94, 40, 258)]
    assert not phases[0]['with_enemy'] and phases[1]['with_enemy']
    return phases


def same_mini(before, after):
    assert before['cadence'] == after['cadence'] == dict(physical=3494, updates=3494, lag_nmi=0, zero_update=0)
    assert before['lifts'] == after['lifts']
    assert {k: v for k, v in before['audio'].items() if k != 'ROM_sha256'} == {
        k: v for k, v in after['audio'].items() if k != 'ROM_sha256'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    rom, cpu = ROOT / 'candidate.nes', read(CPU)
    assert cpu['passed'] and cpu['parent_SHA256'] == sha(SPARSE) == SPARSE_SHA
    assert sha(rom) == cpu['expected_memory_only_SHA256'] == PIN
    bindings({str(R / p): h for p, h in cpu['bindings'].items()})
    row, = cpu['patches']
    start = row['file_offset']
    old, new = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
    before = SPARSE.read_bytes()
    assert row['physical_PRG'] == 33 and row['CPU_half_open'] == [0xbea2, 0xbf00]
    assert before[start:start + len(old)] == old and len(old) == len(new)
    assert rom.read_bytes() == before[:start] + new + before[start + len(old):]
    openings = {}
    for name, owner, baseline, trial in (('bill', 3, (1, 28), (1, 19)), ('samus', 2, (0, 18), (0, 14))):
        candidate = ROOT / f'candidate-{name}'
        bindings(read(candidate / 'ready.json')['bindings'])
        openings[name] = dict(baseline=opening(PRIOR / name, SPARSE_SHA, owner, baseline),
                              candidate=opening(candidate, PIN, owner, trial))
    mini = mini_evidence(ROOT / 'mini', PIN)
    # Prior replay is already verified, but its packet helper is a historical source revision.
    prior = read(R / 'build/shared-sparse-draw-delivery-1110/verified-delivery.json')
    assert prior['Downloads_launch_verified'] and prior['ROM_SHA256'] == SPARSE_SHA
    same_mini(dict(audio=read(PRIOR / 'mini/capture/audio-order.json'),
                   cadence=prior['mini_active_cadence'], lifts=prior['native_lifts']), mini)
    assert check(NIGHTLY)['ROM_sha256'] == SPARSE_SHA
    preflight(reserved_files=70, fresh=True)
    out.mkdir()
    metadata = out / 'candidate-proof.json'
    metadata.write_text(json.dumps(dict(candidate_SHA256=PIN, CPU_SHA256=sha(CPU), openings=openings), indent=2) + '\n')
    try:
        installer('install', out, rom, ROOT, SPARSE_SHA, SPARSE, metadata)
        packet = out / 'downloads-smoke'
        run([str(packet / 'run.py')])
        assert mini_evidence(packet, PIN) == mini
        assert read(packet / 'capture/timing.json') == read(ROOT / 'mini/capture/timing.json')
        installer('finalize', out, rom, ROOT, SPARSE_SHA, SPARSE, metadata)
    except Exception:
        NIGHTLY.write_bytes(before)
        assert check(NIGHTLY)['ROM_sha256'] == SPARSE_SHA
        raise

    receipt_path = out / 'verified-delivery.json'
    receipt, ips = read(receipt_path), out / ASSET
    assert receipt['ROM_SHA256'] == check(NIGHTLY)['ROM_sha256'] == PIN
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['IPS_SHA256'] == sha(ips)
    notes = out / 'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\n'
                     'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
                     f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {PIN}\n\n'
                     'Shared side collision skips unused Mario the Tank bank switches. '
                     'The same 1-1 opening replays reduced Bill’s walking misses from 28 to 19 '
                     'and Samus’s from 18 to 14. Mini cleared 1-1 with both lives and zero active misses.\n',
                     encoding='utf-8')
    subprocess.run(['gh', 'release', 'upload', 'Current', str(ips), '--clobber', '--repo', REPO], check=True)
    subprocess.run(['gh', 'release', 'edit', 'Current', '--latest', '--notes-file', str(notes), '--repo', REPO], check=True)
    remote = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases/latest'], encoding='utf-8'))
    asset, = remote['assets']
    assert remote['tag_name'] == 'Current' and asset['name'] == ASSET
    assert asset['digest'] == 'sha256:' + receipt['IPS_SHA256']
    receipt.update(shared_openings=openings, mini_active_cadence=mini['cadence'], native_lifts=mini['lifts'],
                   release_tag='Current', release_is_latest=True, sole_asset=ASSET,
                   release_asset_digest=asset['digest'], final_patch_guard=check(NIGHTLY))
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Downloads and Current IPS verified for {PIN}', flush=True)


if __name__ == '__main__':
    main()
