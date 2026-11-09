"""Deliver the exact shared sparse-draw build after matched native replays."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from build_storage_guard_v1 import preflight
from deliver_helper_camera_render_1110 import mini_evidence, read, run
import deliver_mini_nightly_root_1103_v30 as Nightly
from prepare_selected_native_packet_v1 import R, sha


ROOT = R / 'build/shared-sparse-draw-native-1110'
PARENT = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
PIN = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
REPO = 'kandowontu2/SMB-Crossover'
ASSET = 'SMB-Crossover-Latest-WIP-MMC5.ips'


def installer(action, out, rom, root=ROOT, parent=PARENT, symbols=None, metadata=None):
    original = Nightly.O, Nightly.PREVIOUS, sys.argv
    try:
        Nightly.O, Nightly.PREVIOUS = out, parent
        sys.argv = [str(Path(Nightly.__file__)), action, '--rom', str(rom),
                    '--packet', str(root / 'mini'), '--candidate', str(metadata or root / 'proof.json')]
        if symbols:
            sys.argv.extend(('--symbols-from', str(symbols)))
        Nightly.main()
    finally:
        Nightly.O, Nightly.PREVIOUS, sys.argv = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--combined-proof', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    rom, native = ROOT / 'candidate.nes', read(ROOT / 'proof.json')
    composed = read(args.combined_proof)
    assert composed['passed'] and composed['parent_SHA256'] == PARENT
    assert composed['expected_memory_only_SHA256'] == native['candidate_SHA256'] == sha(rom) == PIN
    for name, expected in (('bill', (1, 28)), ('samus', (0, 18))):
        result = ROOT / name / 'capture/result.json'
        assert sha(result) == native['results'][name]['candidate_SHA256']
        bound = read(result.with_name('binding.json'))
        assert bound['exit_code'] == 0 and bound['ROM_sha256'] == PIN
        assert tuple(p['no_controller_read'] for p in read(result)['phases']) == expected
    mini = mini_evidence(ROOT / 'mini', PIN)
    cadence = mini['cadence']
    assert cadence == dict(physical=3494, updates=3494, lag_nmi=0, zero_update=0)
    assert Nightly.check(Nightly.D)['ROM_sha256'] == PARENT
    previous = Nightly.D.read_bytes()
    preflight(reserved_files=70, fresh=True)
    try:
        installer('install', out, rom)
        packet = out / 'downloads-smoke'
        run([str(packet / 'run.py')])
        assert mini_evidence(packet, PIN) == mini
        assert read(packet / 'capture/timing.json') == read(ROOT / 'mini/capture/timing.json')
        installer('finalize', out, rom)
    except Exception:
        Nightly.D.write_bytes(previous)
        assert Nightly.check(Nightly.D)['ROM_sha256'] == PARENT
        raise
    patch = out / ASSET
    receipt_path = out / 'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['ROM_SHA256'] == Nightly.check(Nightly.D)['ROM_sha256'] == PIN
    assert receipt['IPS_roundtrip'] and receipt['Downloads_launch_verified'] and not receipt['backup_created']
    assert receipt['IPS_SHA256'] == sha(patch)
    receipt.update(shared_openings=native['results'], mini_active_cadence=cadence,
                   combined_CPU_proof_SHA256=sha(args.combined_proof), native_lifts=mini['lifts'],
                   verification_scope='Bill and Samus controller-only Easy 1-1 opening and actual Downloads Mini '
                                      'nonshortcut 1-1 with all three lifts, both lives and zero active lag.')
    notes = out / 'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\n'
                     'Apply the IPS to clean, headered Super Mario Bros. (World).\n'
                     f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {PIN}\n\n'
                     'The shared renderer skips unnecessary firebar and projectile checks. '
                     'Matched Mesen opening replays reduced Bill’s idle missed reads from 3 to 1 '
                     'and Samus’s walking misses from 22 to 18. Mini Mario cleared 1-1 '
                     'with both lives and zero missed reads in 3,494 active frames.\n', encoding='utf-8')
    subprocess.run(['gh', 'release', 'upload', 'Current', str(patch), '--clobber', '--repo', REPO], check=True)
    subprocess.run(['gh', 'release', 'edit', 'Current', '--latest', '--notes-file', str(notes), '--repo', REPO], check=True)
    remote = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases/latest'], text=True, encoding='utf-8'))
    assert remote['tag_name'] == 'Current' and len(remote['assets']) == 1
    asset = remote['assets'][0]
    assert asset['name'] == ASSET and asset['digest'] == 'sha256:' + sha(patch)
    receipt.update(release_tag='Current', release_is_latest=True, sole_asset=ASSET,
                   release_asset_digest=asset['digest'], final_patch_guard=Nightly.check(Nightly.D))
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(f'Downloads and Current IPS verified for {PIN}', flush=True)


if __name__ == '__main__':
    main()
