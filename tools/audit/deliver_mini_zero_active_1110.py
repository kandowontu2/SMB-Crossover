"""Deliver the exact Mini route with zero missed active gameplay frames."""

import argparse
import json
from pathlib import Path

from build_storage_guard_v1 import preflight
from check_mini_funded_actor_1108_v3 import install
import deliver_mini_contact_draw_1110 as Delivery
from deliver_helper_camera_render_1110 import bindings, read, run
from prepare_selected_native_packet_v1 import sha


R = Delivery.R
ROOT = R / 'build/mini-contact-platform-combo-native-1110'
PARENT_ROOT = R / 'build/mini-platform-pair-native-1110'
PARENT_RECEIPT = R / 'build/mini-platform-pair-delivery-1110/verified-delivery.json'
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
PREVIOUS = 'df03fc35ebdc516a8df0b501bbe2008e52836aa8fcfad5c34e4df76783e9f331'
PROOF = '9bb145df9aff1a33107d5e49bfc4fad1935df8f29fea3cf01f5baddebf556916'
TIMING = '073139fe0b9b5880737a58ffdcac15d24a523500371545cc4fe012130ab48e58'
ROLE = 'native_player_contact_offset'


def metrics(packet, route):
    result = Delivery.NIGHTLY.proof(packet, PIN)
    timing = packet / 'capture/timing.json'
    assert sha(timing) == TIMING
    t = read(timing)
    cadence = route['cadence']
    assert cadence == t['cadence']['fullstage']
    # The controller's missed-read counter is sparse and is absent when zero.
    normalized = {'no_controller_read': 0, **cadence}
    assert normalized == dict(lag_nmi=0, no_controller_read=0, physical=3494, updates=3494, zero_update=0)
    assert t['ROM_sha256'] == PIN and t['open_calls'] == t['open_interrupts'] == 0
    assert (result['physical_frames'], result['source_updates']) == (5279, 3495)
    assert t['interrupts']['lag_nmi']['calls'] == 70
    assert t['routines']['fullstage']['GameLoop']['calls'] == 3494
    audio = route['audio']
    assert audio['packed_frames'] == audio['packed_status_writes'] == 3369
    assert audio['ordered_music_image_writes'] == 4385 and audio['terminal_tokens'] == 1
    assert audio['apu_writes'] == 14250 and audio['mmc5_audio_writes'] == 5108
    return dict(whole_replay_physical_frames=5279, active_11_cadence=normalized,
                nonactive_lag_nmi=70, foreground_cycles=t['routines']['fullstage']['GameLoop']['foreground'],
                source_audio_frames=audio['packed_frames'], timing_SHA256=sha(timing))


def evidence():
    rom = ROOT / 'candidate.nes'
    manifest = rom.with_suffix('.json')
    path = ROOT / 'proof.json'
    prior = PARENT_ROOT / 'candidate.nes'
    proof, meta, earlier = read(path), read(manifest), read(PARENT_ROOT / 'proof.json')
    assert sha(path) == meta['composed_proof_SHA256'] == PROOF
    assert sha(rom) == proof['candidate_SHA256'] == meta['candidate_SHA256'] == PIN
    assert sha(prior) == earlier['candidate_SHA256'] == PREVIOUS and proof['passed'] and earlier['passed']
    assert proof['groups'] == meta['groups']
    assert {key: rows for key, rows in proof['groups'].items() if key != ROLE} == earlier['groups']
    assert proof['final_minus_SHA256'][ROLE] == PREVIOUS
    row, = proof['groups'][ROLE]
    assert (row['physical_PRG'], row['CPU_half_open'], row['file_offset']) == (126, [0x9659, 0x9690], 1037929)
    assert install(prior.read_bytes(), [row]) == rom.read_bytes()
    bindings(proof['bindings'])
    receipt = read(PARENT_RECEIPT)
    assert receipt['ROM_SHA256'] == PREVIOUS and receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip']
    assert receipt['active_11_cadence']['no_controller_read'] == 2
    assert Delivery.NIGHTLY.check(Delivery.NIGHTLY.D)['ROM_sha256'] == PREVIOUS

    for name in ('mini', *(f'native/{name}' for name in Delivery.Parent.Suites.PACKETS)):
        ready = read(ROOT / name / 'ready.json')
        assert ready['ROM_sha256'] == PIN and Path(ready['ROM']).resolve() == rom
        assert not ready['emulated_writes']
        bindings(ready['bindings'])
        source = (PARENT_ROOT / name / 'controller.lua').read_text(encoding='utf-8')
        candidate = (ROOT / name / 'controller.lua').read_text(encoding='utf-8')
        assert source.count(PREVIOUS) == 1 and candidate == source.replace(PREVIOUS, PIN, 1)

    with Delivery.validators(PIN) as validation:
        validation.native_suite(ROOT, rom)
        route = validation.route_evidence(ROOT / 'mini')
        injury = Delivery.Parent.Prior.corrected_injury(ROOT / 'native/injury', rom)
    handoff = read(ROOT / 'native/injury/capture/result.json')['injury_helper']['handoff_dma']
    assert handoff['page'] == 2 and handoff['draw_engine'] == 10 and handoff['actual'] == handoff['expected']
    assert handoff['stale_actual'] != handoff['stale_expected']
    assert handoff['counter'] == (handoff['draw_counter'] + 1) & 255
    assert [(q['left'], q['top']) for q in route['camera_edge_spawns']] == [(560, 192), (688, 192), (864, 192)]
    return rom, manifest, route, metrics(ROOT / 'mini', route), dict(injury, handoff_dma=handoff)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--check-only', action='store_true')
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build' and not out.exists()
    rom, manifest, route, tested, injury = evidence()
    if args.check_only:
        print(json.dumps(dict(ready=True, ROM_SHA256=PIN, native=tested)), flush=True)
        return

    preflight(reserved_files=69, fresh=True)
    old = Delivery.Parent.PREVIOUS
    Delivery.Parent.PREVIOUS = PREVIOUS
    try:
        Delivery.Parent.installer('install', out, rom, ROOT / 'mini', manifest)
        packet = out / 'downloads-smoke'
        assert Path(read(packet / 'ready.json')['ROM']).resolve() == Delivery.NIGHTLY.D.resolve()
        assert sha(packet / 'controller.lua') == sha(ROOT / 'mini/controller.lua')
        run([str(packet / 'run.py')])
        with Delivery.validators(PIN) as validation:
            downloads = validation.route_evidence(packet)
        assert downloads == route and metrics(packet, downloads) == tested
        Delivery.Parent.installer('finalize', out, rom, ROOT / 'mini', manifest)
    finally:
        Delivery.Parent.PREVIOUS = old

    path = out / 'verified-delivery.json'
    receipt = read(path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['ROM_SHA256'] == Delivery.NIGHTLY.check(Delivery.NIGHTLY.D)['ROM_sha256'] == PIN
    assert receipt['IPS_SHA256'] == sha(out / 'SMB-Crossover-Latest-WIP-MMC5.ips')
    receipt.update(active_11_cadence=tested['active_11_cadence'], native_lifts=downloads['lifts'],
                   camera_edge_spawns=downloads['camera_edge_spawns'], camera_edge_spawns_match_candidate=True,
                   native_audio=downloads['audio'], native_audio_matches_candidate=True, native_corrected_injury=injury,
                   native_performance=tested,
                   verification_scope='Controller-only Downloads Mini 1-1 into 1-2 with zero active lag, all three lift '
                                      'crossings, both lives, source audio voice order, idle, power, fire and injury. '
                                      'Loading and transition lag is measured separately.')
    path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (out / 'release-notes.txt').write_text(
        'Current MMC5 work-in-progress nightly.\n\n'
        'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
        f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {PIN}\n\n'
        'Mini Mario cleared 1-1 to 1-2 with both lives and zero missed controller reads across 3,494 '
        'active gameplay frames. This test covers one full route. Loading and stage transitions '
        'still have lag. Reopen the ROM and start a fresh game.\n', encoding='utf-8')
    print(json.dumps(dict(delivered=True, ROM_SHA256=PIN, IPS_SHA256=receipt['IPS_SHA256'], native=tested)), flush=True)


if __name__ == '__main__':
    main()
