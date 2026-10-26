"""Freeze the first flower replay failure; read saved evidence only, never Mesen."""
from pathlib import Path
import argparse
import csv
import hashlib
import itertools
import json

from PIL import Image, ImageDraw
from py65.devices.mpu6502 import MPU
from check_tmnt_render_oa import address, load, location


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    return list(csv.DictReader(Path(path).open(encoding='utf-8')))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def actual_shuffle(bundle, before, parity, objects):
    """Execute the compiled allocation order, trapping only draw bodies."""
    m = [0] * 65536
    m[0xa000:0xc000] = bundle['raw'][16 + 4 * 8192:16 + 5 * 8192]
    m[address(bundle, 'SpriteShuffleOffset')] = before
    m[address(bundle, 'FrameCounter')] = parity
    for index in objects:
        m[address(bundle, 'ObjectMetasprite') + index] = 1
    c = MPU(memory=m, pc=address(bundle, 'InitObjectLoop'))
    c.sp = 0xfd
    order = []
    for count in range(1000):
        if c.pc == address(bundle, 'HandleFloateyNumbers'):
            return order, c.a, count
        if c.pc in [address(bundle, 'DrawMetasprite'), address(bundle, 'WorldFirebarDrawAdmission')]:
            if c.pc == address(bundle, 'DrawMetasprite'):
                order.append(objects[c.y])
            c.pc = c.stPopWord() + 1
        else:
            c.step()
    raise AssertionError('Compiled object-order loop did not terminate')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(a.rom) == '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'
    native = a.packet / 'mario-easy'
    readiness = json.loads((a.packet / 'readiness.json').read_text())
    assert sha(a.packet / 'readiness.json') == 'dfe16a41b0b83c1dd16b3386afaf2859152751e361807fcd56d75b7a7b7501fd'
    assert sha(a.packet / 'ROOT-grant.json') == '6e0ac81b2f5ee0f3834fc2236e9ffca44010bf3d105af0e922cbf7d3c5cc0c34'
    assert all(sha(k) == v for k, v in readiness['bindings'].items()), 'Frozen preparation binding drift'
    original = json.loads((a.packet / 'native-proof.json').read_text())
    assert original['passed'] is False and original['profiles_run'] == 1
    assert original['native_worker_released'] is True
    assert original['profiles'][0]['exit'] == 1 and original['profiles'][0]['retries'] == 0
    assert 'Retain power; no injury masquerading as progression' in (native / 'candidate-run.log').read_text()
    assert not (native / 'flower-component.json').exists()

    trace = {int(r['frame']): r for r in rows(native / 'trace.csv')}
    render = {int(r['frame']): r for r in rows(native / 'render.csv')}
    state = {int(r['frame']): r for r in rows(native / 'flower-state.csv')}
    owner = [json.loads(line) for line in (native / 'flower-owner.jsonl').read_text().splitlines()]
    assert [(r['kind'], r.get('itemIndex'), r['frame']) for r in owner] == [
        ('real-block-reveal', 1, 694), ('real-native-collection', 1, 839), ('real-block-reveal', 2, 1346)]
    growth = [r for r in state.values() if int(r['growing']) and 840 <= int(r['frame']) <= 899]
    assert len(growth) == 60 and [int(r['age']) for r in growth] == list(range(60))
    assert {(r['x'], r['y']) for r in growth} == {('413', '176')}
    assert state[900]['power'] == '1' and state[900]['growing'] == '0'
    assert state[1394]['engine'] == '8' and state[1395]['engine'] == '9'
    assert state[1395]['growing'] == '1' and state[1395]['age'] == '0'
    assert state[1395]['actors'] == '5:14:1:1248:123'
    assert state[1395]['collected'] == '1' and state[1395]['shot0'] == state[1395]['shot1'] == '0'

    # Distinguish the two ordinary two-piece Goombas by horizontal continuity.
    # A is the left/falling one; B is the right one. F is known delivery slot5.
    orders, evidence = [], []
    for r in rows(native / 'oam.csv'):
        frame = int(r['frame'])
        if not 1363 <= frame <= 1395:
            continue
        data, camera = bytes.fromhex(r['oamHex']), int(r['camera'])
        goomba, flower = [], []
        for i in range(4, 64):
            y, tile, attr, x = data[i * 4:i * 4 + 4]
            if y < 240 and tile in [0xa2, 0xa4]:
                assert attr & 3 == 3
                goomba.append((i, camera + x, y))
            if y < 240 and tile == 0x78:
                flower.append(i)
        assert len(goomba) == 4 and len(flower) == 2
        pairs = [dict(oam_first=goomba[i][0], x=min(v[1] for v in goomba[i:i + 2]),
                      y=goomba[i][2]) for i in [0, 2]]
        left, right = sorted(pairs, key=lambda z: z['x'])
        order = ''.join(k for _, k in sorted([(left['oam_first'], 'A'),
                        (right['oam_first'], 'B'), (min(flower), 'F')]))
        assert int(render[frame]['dmaCount']) == 1 and render[frame]['lagNmi'] == '0'
        assert trace[frame]['nmiSkipped'] == '7'
        assert int(trace[frame]['poll']) == frame - 1
        orders.append((frame, order))
        evidence.append(dict(frame=frame, actual_oam_order=order, falling_goomba=left,
                             other_goomba=right, mario_x=int(trace[frame]['x']),
                             mario_y=int(trace[frame]['y']), vx_raw=int(trace[frame]['vx']),
                             input_mask=int(trace[frame]['buttons']), engine=int(trace[frame]['engine'])))
    assert len(orders) == 33
    candidates = []
    for left, right in itertools.permutations(range(1, 6), 2):
        objects = {left: 'A', right: 'B', 6: 'F'}
        for before, parity in itertools.product(range(24), range(2)):
            predicted = []
            for i in range(len(orders)):
                start = (before + 19 * (i + 1)) % 24
                step = 13 if (parity + i) % 2 else -13
                predicted.append(''.join(objects[v] for j in range(24)
                                 if (v := (start + step * (j + 1)) % 24) in objects))
            if predicted == [order for _, order in orders]:
                candidates.append(dict(falling_enemy_slot=left - 1, other_enemy_slot=right - 1,
                                       before_first_draw_shuffle=before, first_FrameCounter_parity=parity))
    assert candidates == [dict(falling_enemy_slot=0, other_enemy_slot=1,
                              before_first_draw_shuffle=3, first_FrameCounter_parity=0)]
    bundle = load(a.rom)
    actual_rows = []
    for i, (frame, expected) in enumerate(orders):
        before = (3 + 19 * i) % 24
        actual, after, instructions = actual_shuffle(bundle, before, i % 2, {1: 'A', 2: 'B', 6: 'F'})
        assert ''.join(actual) == expected and after == (before + 19) % 24
        actual_rows.append(dict(frame=frame, predicted_and_compiled_order=expected,
                               compiled_final_shuffle=after, instruction_count=instructions))
    compiled = bundle['raw'][location(bundle, 'InitObjectLoop'):location(bundle, 'HandleFloateyNumbers')]
    source = a.rom.parent / 'source/src'
    write(a.output / 'contact-evidence.json', dict(
        passed=True, saved_evidence_only=True, new_native_launches=0,
        coordinates='World-camera + actual OAM left edge and raw OAM Y; not sampled Enemy_Y_Position or collision-X registers',
        contact_window=[1384, 1395], every_frame_oam=evidence,
        slot_inference=dict(result=candidates[0], exact_matching_assignments=1,
            observations=33, enumerated_assignments=960, actual_compiled_shuffle_calls=33,
            compiled_calls=actual_rows, compiled_loop_sha256=hashlib.sha256(compiled).hexdigest(),
            compiled_loop_bank=4, compiled_loop_address=address(bundle, 'InitObjectLoop'),
            actual_native_slot_capture=False,
            assumptions='Known physical flower slot5; exactly two continuously tracked Goomba pairs; all33 frames have fresh DMA/no lag and one Main update; native Mario nonrotated24-object shuffle',
            source_cpu_scope='Only actual compiled allocation-order instructions execute; DrawMetasprite and empty world-firebar body are trapped. No collision/PPU/IRQ CPU replay.'),
        source_bindings={str(source / n): sha(source / n) for n in ['metasprite_engine.s', 'metasprite.s', 'native_goomba_draw.s', 'memory.s', 'game.s', 'mario_source.s', 'collision.s']},
        first_failure='Native injury while blind flower-mount/back controller countersteers below falling Goomba; correct no-injury assertion, not established engine defect'))

    selected = [native / 'entered-1-1.png', native / 'frames/000696.png', native / 'growth-1-840.png',
                native / 'growth-1-870.png', native / 'growth-1-899.png', native / 'frames/001200.png',
                native / 'frames/001344.png', native / 'frames/001352.png', native / 'frames/001368.png',
                native / 'frames/001384.png', native / 'frames/001392.png', native / 'growth-1-1395.png']
    sheet = Image.new('RGB', (3 * 512, 4 * 268 * 2), '#172132')
    draw = ImageDraw.Draw(sheet)
    selected_rows = []
    for i, path in enumerate(selected):
        image = Image.open(path).convert('RGB')
        assert image.size == (256, 240)
        x, y = i % 3 * 512, i // 3 * 536
        sheet.paste(image.resize((512, 480), Image.Resampling.NEAREST), (x, y + 42))
        draw.text((x + 8, y + 10), path.name, fill='white')
        selected_rows.append(dict(path=str(path), sha256=sha(path), label=path.name))
    sheet.save(a.output / 'partial-progression-and-contact.png')
    write(a.output / 'selected-images.json', dict(placements=12, unique_actual_ppu_frames=12,
        screenshot_scope='12 sampled frames including3 actual injury approach endpoints; not everyframe visual review', images=selected_rows))

    config = json.loads((native / 'configuration.json').read_text())['item']
    audio = rows(native / 'audio-events.csv')
    requests = {name: sum(r['event'] == 'Square2SoundQueue' and int(r['value']) & mask != 0
                         for r in audio) for name, mask in config['sfx'].items() if name != 'fire'}
    requests['fire_after_Fire_status'] = 0

    original_files = [v for v in a.packet.rglob('*') if v.is_file() and a.output not in v.parents]
    bindings = {str(v): sha(v) for v in original_files}
    bindings.update({str(Path(__file__).resolve()): sha(__file__), str(a.report): sha(a.report)})
    bindings.update({str(v): sha(v) for v in a.output.iterdir() if v.is_file()})
    write(a.output / 'proof.json', dict(
        analysis_passed=True, native_passed=False, status='FIRST_FAILURE_PRESERVED',
        ROM_sha256=sha(a.rom), original_preparation_bindings_reverified=len(readiness['bindings']),
        native_launches=1, retries=0, new_launches_in_this_postprocessor=0,
        native_worker_released=True, actual_character=0, actual_variant=0, actual_numeric_mode=0,
        coverage=dict(first_mushroom_reveal_frame=694, first_physical_collection_frame=839,
            first_transform_updates=60, first_transform_fixed_position=[413,176], retained_Super_frame=900,
            later_block_reveal_frame=1346, actual_flower_active_after_reveal=True,
            flower_collected=False, second_transform_updates=0, Fire_obtained=False,
            fireball_use=False, first_injury_endFrame=1395, final_power=1,
            final_power_is_pre_shrink_injury_start=True, final_flower='slot5/state14/type1/world1248/y123'),
        sound_request_store_counts=requests,
        sound_scope='Raw queue writes include driver shifts/replays, not distinct audible cues or source-waveform proof; no Fire status/use occurred',
        partial_guards=dict(actual_mode_readbacks=sorted({int(r['behaviorVersion']) for r in render.values()}),
            chr_commit_rows=len(rows(native/'chr-commit.csv')),
            chr_bad_rows=sum(int(r.get('bad','0')) for r in rows(native/'chr-commit.csv')),
            original_motion_final_json=json.loads((native/'completed-loop-motion.json').read_text()),
            final_success_or_full_chr_receipt_exists=False),
        cause='Replay controller alignment exposure to falling Goomba; no game defect established',
        smallest_next_step='Controller-only flower-mount/back: inspect live nearest enemy before countersteering/stopping or jumping, retreat left until the proposed vertical-jump body clears the descending Goomba by8px, then use the existing rise/onto phases. Preserve every native guard; freeze/source-review before any newly granted single attempt.',
        no_game_source_settings_or_production_mutations=True,
        no_source_waveform_all_item_fullroute_or_everyframe_visual_claim=True,
        bindings=bindings))
    print(json.dumps(dict(analysis_passed=True, native_passed=False,
        frozen_bindings=len(bindings), proof=str(a.output/'proof.json'),
        proof_sha256=sha(a.output/'proof.json'), worker_released=True), indent=2))


if __name__ == '__main__':
    main()
