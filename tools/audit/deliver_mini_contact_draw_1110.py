"""Deliver an exact, native-qualified shared contact and sprite setup build."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path

import deliver_mini_parser_audio_1110 as Parent
from deliver_helper_camera_render_1110 import bindings, read, run
from prepare_mini_contact_tank_precheck_native_1110 import PARENT_DELIVERY, ROLE
from prepare_selected_native_packet_v1 import sha


R, PREVIOUS = Parent.R, Parent.PIN
ROOT = R / 'build/mini-contact-draw-native-1110'
NIGHTLY = Parent.Nightly


@contextmanager
def validators(pin):
    old = Parent.Prior.PIN
    Parent.Prior.PIN = pin
    try:
        with Parent.Prior.native_validators() as validation:
            yield validation
    finally:
        Parent.Prior.PIN = old


def metrics(packet, pin, route):
    misses = route['cadence']['no_controller_read']
    assert 0 <= misses <= 5
    Parent.EXPECTED_MISSES[pin] = misses
    return Parent.native_metrics(packet, pin, route)


def same_audio(previous, current):
    return ({k: v for k, v in previous['audio'].items() if k != 'ROM_sha256'} ==
            {k: v for k, v in current['audio'].items() if k != 'ROM_sha256'})


def evidence(root, *, installed=False):
    rom = root / 'candidate.nes'
    manifest_path, proof_path = rom.with_suffix('.json'), root / 'proof.json'
    manifest, proof = read(manifest_path), read(proof_path)
    pin = sha(rom)
    assert pin == manifest['candidate_SHA256'] == proof['candidate_SHA256']
    assert manifest['composed_proof_SHA256'] == sha(proof_path)
    assert proof['passed'] and proof['parent_SHA256'] == PREVIOUS
    assert proof['groups'] == manifest['groups'] and set(proof['groups']) == set(proof['final_minus_checks'])
    assert {row['physical_PRG'] for rows in proof['groups'].values() for row in rows} == {26, 78}
    assert ROLE in proof['groups'] and sum(len(rows) for rows in proof['groups'].values()) == 2
    bindings(proof['bindings'])
    published = read(PARENT_DELIVERY)
    assert published['Downloads_launch_verified'] and published['ROM_SHA256'] == PREVIOUS
    assert NIGHTLY.check(NIGHTLY.D)['ROM_sha256'] == (pin if installed else PREVIOUS)
    for name in ('mini', *(f'native/{name}' for name in Parent.Suites.PACKETS)):
        ready = read(root / name / 'ready.json')
        assert ready['ROM_sha256'] == pin and Path(ready['ROM']).resolve() == rom
        assert not ready['emulated_writes']
        bindings(ready['bindings'])
        before = (Parent.ROOT / name / 'controller.lua').read_text(encoding='utf-8')
        after = (root / name / 'controller.lua').read_text(encoding='utf-8')
        assert before.count(PREVIOUS) == 1 and after == before.replace(PREVIOUS, pin, 1)

    with validators(pin) as validation:
        validation.native_suite(root, rom)
        candidate = validation.route_evidence(root / 'mini')
        injury = Parent.Prior.corrected_injury(root / 'native/injury', rom)
    witness = read(root / 'native/injury/capture/result.json')['injury_helper']
    handoff = witness['handoff_dma']
    assert handoff['page'] == 2 and handoff['draw_engine'] == 10
    assert handoff['actual'] == handoff['expected'] and handoff['stale_actual'] != handoff['stale_expected']
    assert handoff['counter'] == (handoff['draw_counter'] + 1) & 255
    assert witness['oam_clears'] > 0 and witness['observed_injury_dmas'] > 0
    with Parent.validators() as validation:
        previous = validation.route_evidence(Parent.ROOT / 'mini')
    before, after = metrics(Parent.ROOT / 'mini', PREVIOUS, previous), metrics(root / 'mini', pin, candidate)
    saved = before['active_GameLoop_foreground'] - after['active_GameLoop_foreground']
    assert saved > 0 and same_audio(previous, candidate)
    assert [(q['left'], q['top']) for q in candidate['camera_edge_spawns']] == [(560, 192), (688, 192), (864, 192)]
    return rom, manifest_path, candidate, dict(injury, handoff_dma=handoff), before, after, saved


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate', type=Path, default=ROOT)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--check-only', action='store_true')
    cli.add_argument('--resume-installed', action='store_true')
    args = cli.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build' and out.exists() == args.resume_installed
    rom, manifest, candidate, injury, before, after, saved = evidence(root, installed=args.resume_installed)
    pin, cadence = sha(rom), candidate['cadence']
    if args.check_only:
        print(json.dumps(dict(ready=True, ROM_SHA256=pin, cadence=cadence, foreground_cycles_saved=saved)), flush=True)
        return

    old = Parent.PREVIOUS
    Parent.PREVIOUS = PREVIOUS
    try:
        installed = out / 'downloads-smoke'
        if args.resume_installed:
            receipt = read(out / 'delivery.json')
            assert receipt['installed'] and not receipt['Downloads_launch_verified'] and not receipt['backup_created']
            assert receipt['previous_ROM_SHA256'] == PREVIOUS and receipt['ROM_SHA256'] == pin
            assert Path(receipt['destination']).resolve() == NIGHTLY.D.resolve()
            assert not (installed / 'capture').exists()
        else:
            Parent.installer('install', out, rom, root / 'mini', manifest)
        assert Path(read(installed / 'ready.json')['ROM']).resolve() == NIGHTLY.D.resolve()
        assert sha(installed / 'controller.lua') == sha(root / 'mini/controller.lua')
        run([str(installed / 'run.py')])
        with validators(pin) as validation:
            downloads = validation.route_evidence(installed)
        assert downloads == candidate and metrics(installed, pin, downloads) == after
        assert read(installed / 'capture/timing.json') == read(root / 'mini/capture/timing.json')
        Parent.installer('finalize', out, rom, root / 'mini', manifest)
    finally:
        Parent.PREVIOUS = old

    path = out / 'verified-delivery.json'
    receipt = read(path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256'] == NIGHTLY.check(NIGHTLY.D)['ROM_sha256'] == pin
    assert receipt['IPS_SHA256'] == sha(out / 'SMB-Crossover-Latest-WIP-MMC5.ips')
    receipt.update(active_11_cadence=cadence, native_lifts=downloads['lifts'],
                   camera_edge_spawns=downloads['camera_edge_spawns'], camera_edge_spawns_match_candidate=True,
                   native_audio=downloads['audio'], native_audio_matches_candidate=True, native_corrected_injury=injury,
                   native_performance=dict(previous=before, current=after, foreground_cycles_saved=saved),
                   verification_scope='Exact Downloads non-shortcut Mini 1-1 into 1-2, both lives and all three native '
                                      'lift crossings. Idle/movement, earned mushroom, both GBC fireballs and injury pass.')
    path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (out / 'release-notes.txt').write_text(
        'Current MMC5 work-in-progress nightly.\n\n'
        'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
        f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {pin}\n\n'
        f'The shared sprite setup and contact checks save {saved:,} foreground CPU cycles over the full Mini 1-1 route. '
        f'The Downloads replay recorded {cadence["no_controller_read"]} lag frames over '
        f'{cadence["physical"]:,} active frames and cleared to 1-2 with both lives. '
        'All three native lifts enter at the camera edge. Reopen the ROM and start a fresh game.\n', encoding='utf-8')
    print(json.dumps(dict(delivered=True, ROM_SHA256=pin, IPS_SHA256=receipt['IPS_SHA256'], cadence=cadence)), flush=True)


if __name__ == '__main__':
    main()
