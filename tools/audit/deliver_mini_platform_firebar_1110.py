"""Deliver the qualified Mini platform, world draw and projection build."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

import deliver_mini_nightly_root_1103_v30 as delivery
import prepare_mini_platform_firebar_native_1110 as composition
from prepare_mini_lane_audio_native_1110 import without_component
from prepare_selected_native_packet_v1 import R, sha


PIN = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
PREVIOUS = '705906f45d3e09d5ebed30f2a9ac15295283a0ca41eb00879ce08fb2f020c7fe'
LIFTS = ((560,576,192,32), (688,704,192,32), (864,880,192,32))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, payload):
    path.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')


def verify_vectors(path, rom, image):
    proof = read(path)
    assert proof['passed'] is True and proof['ROM_written'] is False
    assert proof['candidate_SHA256'] == PIN and proof['parent_SHA256'] == PREVIOUS
    bindings = {Path(name).resolve(): digest for name,digest in proof['bindings'].items()}
    required = (rom, composition.CURRENT, *composition.RECEIPTS,
                R/'tools/audit/prepare_mini_platform_firebar_native_1110.py',
                R/'tools/audit/check_mini_platform_firebar_composed_1110.py')
    assert all(p.resolve() in bindings for p in required)
    for file, digest in bindings.items():
        assert sha(file) == digest, file
    for name, component in zip(('platform','firebar','projection'), composition.COMPONENTS, strict=True):
        assert proof[f'final_minus_{name}_SHA256'] == composition.digest(without_component(image, component))
    direct, firebar, projection = (proof[name] for name in
                                   ('direct_platform','firebar_admission','mini_projection'))
    assert not direct['game_loop']['reads'] and not direct['game_loop']['residual_at_GameLoop_return']
    assert any(row['catchup_skips'] == 1 for row in direct['actual_idle_loop']['cases'])
    assert firebar['vectors']['ISR_APU_mapper_OAM_writes_exact']
    assert {row['id'] for row in firebar['draws']['positive_draws'] if row['OAM_writes'] > 0} == (
        set(range(0x1b,0x23)) | {0x2b,0x2c})
    cuts = {name: group['vectors']['cuts'] for name, group in
            (('platform',direct), ('firebar',firebar), ('projection',projection))}
    for name, lag_key in (('platform','lag_FF'), ('firebar','lag_FF'), ('projection','FF')):
        assert all(cuts[name][key] > 0 for key in ('IRQ', lag_key, 'nested_IRQ'))
    assert all(cuts['platform'][key] > 0 for key in ('poisoned_lag_FF','poisoned_IRQ','poisoned_nested'))
    return cuts


def route_evidence(packet):
    route = delivery.proof(packet, PIN)
    assert route['full_stage'] and route['helpers_added'] and route['last']['lives'] == 2
    last = route['terminal_native']
    fields = ('SelectedCharacter', 'WorldNumber', 'LevelNumber', 'GameEngineSubroutine',
              'OperMode', 'OperMode_Task', 'NumberofLives')
    assert tuple(last[name] for name in fields) == (41,0,1,8,1,3,2)
    stage = route['phases']['fullstage']
    assert stage['wall_restarts'] == 0
    lifts = stage['lifts']
    assert tuple((p['left'],p['center'],p['spawn_top'],p['width']) for p in lifts) == LIFTS
    for lift in lifts:
        assert lift['stage'] == '1-1' and lift['initial_top'] == lift['spawn_top']
        assert lift['boarded'] and lift['departed'] and lift['boarding_press'] and lift['departure_press']
        assert lift['spawn_frame'] < lift['board_frame'] < lift['departure_frame']
    capture = packet/'capture'
    spawns = read(capture/'camera-lifts.json')
    assert spawns == [dict(frame=p['spawn_frame'], left=p['left'], relative_x=p['spawn_relative_x'],
                          slot=p['slot'], top=p['spawn_top']) for p in lifts]
    assert all(p['relative_x'] >= 256 for p in spawns)
    timing = read(capture/'timing.json')
    assert timing['ROM_sha256'] == PIN
    cadence = timing['cadence']['fullstage']
    assert tuple(cadence[key] for key in ('no_controller_read','physical','updates')) == (306,3506,3453)
    audio = read(capture/'audio-order.json')
    assert audio['ROM_sha256'] == PIN and audio['packed_frames'] > 3000 and audio['terminal_tokens'] > 0
    assert audio['packed_status_writes'] == audio['packed_frames']
    assert all(audio[k] > 0 for k in ('apu_writes','mmc5_audio_writes','ordered_music_image_writes'))
    return dict(lifts=lifts, camera_edge_spawns=spawns, cadence=cadence, audio=audio)


def native_suite(root, rom):
    for packet in (root/'route', *(root/'native'/name for name in ('idle','power','fire'))):
        ready = read(packet/'ready.json')
        assert Path(ready['ROM']).resolve() == rom.resolve() and ready['ROM_sha256'] == PIN
        if packet.name != 'fire':
            assert ready['bindings'][str(composition.NEW_KERNEL.resolve())] == sha(composition.NEW_KERNEL)
            assert ready['bindings'][str(composition.NEW_KERNEL.with_suffix('.lbl').resolve())] == sha(
                composition.NEW_KERNEL.with_suffix('.lbl'))
    idle, power, fire = (root/'native'/name for name in ('idle','power','fire'))
    delivery.proof(idle, PIN)
    for phase in ('idle','right','left','brake','jump','landing'):
        row = read(idle/'capture/timing.json')['cadence'][phase]
        assert row['physical'] == row['updates'] and row['lag_nmi'] == row.get('no_controller_read',0) == 0
        if phase == 'idle':
            assert row['updates'] == 180
    earned = delivery.proof(power, PIN)['earned_power']
    assert earned['completed'] and earned['mature'] and earned['item_lost']['status'] == 1
    ready = read(fire/'ready.json')
    bind = read(fire/'capture/binding.json')
    result = read(fire/'capture/result.json')
    assert bind['exit_code'] == 0 and bind['ready_sha256'] == sha(fire/'ready.json')
    assert bind['ROM_sha256'] == result['ROM_sha256'] == PIN and result['passed']
    for path, digest in ready['bindings'].items():
        assert sha(Path(path)) == digest, path
    assert result['max_active_fireballs'] == result['max_visible_fireballs'] == 2
    assert result['staged_goomba_hit'] and all(result['concurrent_DMA_by_direction'].values())
    assert result['moving_art_phases'] == {str(i):True for i in range(4)}
    assert result['impact_art_frames'] == {'C':True, 'D':True}


def run(argv):
    result = subprocess.run([sys.executable,'-B',*argv], cwd=R, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout[-1800:], flush=True)
    assert result.returncode == 0, (argv, result.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--vectors', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true', help='Read existing evidence without installing')
    args = parser.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    rom = root/'candidate.nes'
    parent, expected = composition.build_image()
    assert composition.digest(parent) == PREVIOUS and sha(rom) == PIN
    assert rom.read_bytes() == expected
    manifest = read(root/'candidate.json')
    assert manifest['candidate_SHA256'] == PIN and manifest['parent_SHA256'] == PREVIOUS
    assert manifest['kernel_SHA256'] == sha(composition.NEW_KERNEL)
    for suffix in ('.dbg','.lbl'):
        assert sha(rom.with_suffix(suffix)) == sha(composition.CURRENT.with_suffix(suffix))
    cuts = verify_vectors(args.vectors, rom, expected)
    native_suite(root, rom)
    candidate = route_evidence(root/'route')
    assert delivery.check(delivery.D)['ROM_sha256'] == PREVIOUS
    if args.check_only:
        print(json.dumps(dict(ready=True, ROM_SHA256=PIN, cadence=candidate['cadence'], vector_cuts=cuts)), flush=True)
        return

    common = ['--candidate',str(root),'--route',str(root/'route'),
              '--fire',str(root/'native/fire'),'--idle',str(root/'native/idle'),
              '--power',str(root/'native/power'),'--output',str(out),'--previous',PREVIOUS]
    installer = 'tools/audit/deliver_mini_lifts_art_1108.py'
    run([installer,'install',*common])
    installed = out/'downloads-smoke'
    assert Path(read(installed/'ready.json')['ROM']).resolve() == delivery.D.resolve()
    run([str(installed/'run.py')])
    downloads = route_evidence(installed)
    assert downloads == candidate, 'Downloads route, helper or passive audio evidence differs from candidate'
    assert delivery.check(delivery.D)['ROM_sha256'] == PIN
    run([installer,'finalize',*common])

    receipt_path = out/'verified-delivery.json'
    receipt = read(receipt_path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    cadence = candidate['cadence']
    receipt.update(camera_edge_spawn=True, lag_free=False, exact_composed_vectors_SHA256=sha(args.vectors),
                   vector_cuts=cuts, previous_comparable_missed_reads=356,
                   native_audio=downloads['audio'], native_audio_matches_candidate=True,
                   camera_edge_spawns=downloads['camera_edge_spawns'])
    write(receipt_path, receipt)
    notes = out/'release-notes.txt'
    text = notes.read_text(encoding='utf-8')
    text += ('\nFaster native vertical lift motion when Mini is off the lift, world drawing, and Mini collision sweeps. '
             f'The same 1-1 controller recorded {cadence["no_controller_read"]} missed reads '
             f'over {cadence["physical"]} physical frames and {cadence["updates"]} updates. '
             'The previous build recorded 356 missed reads over 3,520 physical frames and 3,453 updates. '
             'The Downloads audio trace matches the candidate replay.\n')
    notes.write_text(text, encoding='utf-8')
    print(json.dumps(dict(delivered=True, ROM_SHA256=PIN, IPS_SHA256=receipt['IPS_SHA256'], cadence=cadence)), flush=True)


if __name__ == '__main__':
    main()
