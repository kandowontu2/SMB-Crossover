"""Analyze/freeze the single granted clean731 east-v4 result; never launch an emulator."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'mario-flower731-east-v1'
N = P / 'mario-easy'
OUT = P / 'native-result-freeze-v1'
READY = 'd138ff82593aa064f1d00873588cb08a79a35acfb3dd812c3bc6cf69b1763a79'
ROM = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def put(p, z):
    assert not p.exists(), ('Preserve existing outcome', p)
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def rows(name):
    with (N / name).open(newline='') as f:
        return list(csv.DictReader(f))


def verify_ready():
    assert sha(P / 'readiness.json') == READY
    q = read(P / 'readiness.json')
    assert len(q['bindings']) == 3145
    for path, h in q['bindings'].items():
        assert sha(path) == h, path
    return q


def sheet(name, images):
    im = Image.new('RGB', (1536, ((len(images) + 2) // 3) * 528), '#172132')
    draw = ImageDraw.Draw(im)
    for i, f in enumerate(images):
        tile = Image.open(f).convert('RGB')
        assert tile.size == (256, 240)
        x, y = i % 3 * 512, i // 3 * 528
        draw.text((x + 8, y + 8), f.name, fill='white')
        im.paste(tile.resize((512, 480), Image.Resampling.NEAREST), (x, y + 36))
    im.save(OUT / name)
    return dict(path=str(OUT / name), sha256=sha(OUT / name), placements=len(images),
                images=[dict(path=str(f), sha256=sha(f)) for f in images])


def analyze():
    verify_ready()
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'component-evidence.json').exists(), 'No silent receipt rewrite'
    native = read(P / 'native-proof.json')
    assert native['passed'] and native['profiles_run'] == 1 and native['native_worker_released']
    assert native['ROM_sha256'] == ROM
    receipt = native['profiles'][0]
    assert receipt['passed'] and receipt['exit'] == 0 and receipt['retries'] == 0
    assert receipt['result']['frames'] == 1945 and receipt['result']['deaths'] == 0
    assert receipt['component'] == read(N / 'flower-component.json')
    assert receipt['CHR']['passed'] and receipt['CHR']['frames'] == 1396
    assert receipt['CHR']['mismatched_frames'] == 0
    owners = [json.loads(s) for s in (N / 'flower-owner.jsonl').read_text().splitlines()]
    pickups = [s for s in owners if s['kind'] == 'real-native-collection']
    assert [(s['frame'], s['type'], s['slot']) for s in pickups] == [(839, 0, 5), (1457, 1, 5)]
    reveals = [s for s in owners if s['kind'] == 'real-block-reveal']
    assert [(s['frame'], s['blockX'], s['playerPower']) for s in reveals] == [(694, 336, 0), (1346, 1248, 1)]
    state = {int(r['frame']): r for r in rows('flower-state.csv')}
    growth = []
    for first, last, xy, collected in [(840, 899, ('413', '176'), '1'), (1458, 1517, ('1259', '107'), '2')]:
        z = [state[f] for f in range(first, last + 1)]
        assert all((r['x'], r['y']) == xy and r['growing'] == '1' and r['collected'] == collected for r in z)
        assert [int(r['age']) for r in z] == list(range(60))
        growth.append(dict(first_frame=first, last_frame=last, source_updates=60, fixed_position=xy))
    assert all(state[f]['power'] == '2' and state[f]['growing'] == '0' for f in range(1518, 1946))
    contacts = [s for s in owners if s['kind'] == 'actual-fireball-enemy-contact']
    assert len(contacts) == 1
    assert {k: contacts[0][k] for k in ['frame', 'enemySlot', 'enemyID', 'state', 'x', 'y']} == dict(
        frame=1898, enemySlot=0, enemyID=6, state=0, x=1682, y=172)
    brick = [s for s in owners if s['kind'] == 'actual-fireball-brick-contact']
    assert len(brick) == 9
    alloc = [s for s in owners if s['kind'] == 'actual-fireball-allocation']
    assert len(alloc) == 20 and len({(s['frame'], s['slot']) for s in alloc}) == 10
    inputs = rows('inputs.csv')
    released = [r for r in inputs if int(r['frame']) >= 1899]
    assert len(released) == 46 and all(r['mask'] == '0' for r in released)
    assert state[1900]['phase'] == 'drain'
    assert state[1906]['shot0'] == '0' and state[1911]['shot1'] == '0'
    assert all(state[f]['shot0'] == '0' and state[f]['shot1'] == '0' for f in range(1911, 1946))
    assert (state[1945]['x'], state[1945]['y'], state[1945]['power']) == ('1682', '176', '2')
    chrrows = rows('chr-commit.csv')
    assert len(chrrows) == 1396 and not any(int(r['bad']) for r in chrrows)
    motion = read(N / 'completed-loop-motion.json')
    assert motion == dict(passed=True, checks=1476, max_world_step=3, max_camera_step=3, game_state_writes=False)
    trace = rows('trace.csv')
    assert {r['lives'] for r in trace if int(r['frame']) >= 347} == {'2'}
    render = rows('render.csv')
    assert {r['behaviorVersion'] for r in render} == {'0'}
    put(OUT / 'component-evidence.json', dict(
        passed=True, ROM_sha256=ROM, native_launches=1, retries=0, native_worker_released=True,
        actual_character=0, actual_variant=0, actual_mode=0, genuine_pickups=pickups,
        genuine_block_reveals=reveals, growth=growth, retained_Fire_from1518_through1945=True,
        actual_live_Goomba_contact=contacts[0], actual_brick_handler_admissions=brick,
        brick_scope='Source handler entry with validated live fireball/tile, not a claim of nine destroyed bricks',
        allocation_write_records=20, unique_frame_slot_groups=10,
        allocation_scope='Raw records repeat. Ten allocation groups are not a separately certified ten-projectile count.',
        no_input_polls_after_contact=46, drain_controller_minimum=45,
        slot0_inactive_from=1906, slot1_inactive_from=1911,
        both_inactive_through_endpoint=True, final_position=[1682, 176], final_power=2,
        raw_sound_request_stores=dict(reveal=8, pickup=4, fire=20),
        sound_scope='Actual source queue stores; repeated shifts are retained. No distinct-audible-cue or waveform claim.',
        CHR=receipt['CHR'], motion=motion, no_game_state_writes=True,
        scope='One exact731 MarioEasy physical mushroom/flower progression, native fireball contact and release/drain; not Hard/Luigi/all-items/fullroute evidence'))
    first = [N / 'frames/000696.png', N / 'growth-1-840.png', N / 'growth-1-870.png', N / 'growth-1-899.png',
             N / 'frames/001352.png', N / 'frames/001408.png', N / 'frames/001424.png', N / 'frames/001448.png',
             N / 'growth-2-1458.png', N / 'growth-2-1488.png', N / 'growth-2-1517.png', N / 'frames/001520.png',
             N / 'frames/001544.png', N / 'frames/001568.png', N / 'frames/001608.png']
    contact = [N / 'frames' / f'{f:06}.png' for f in [1816, 1856, 1872, 1888, 1896, 1904, 1912, 1920, 1928, 1936, 1944]]
    contact.append(N / 'endpoint.png')
    sheets = [sheet('physical-progression-selected15.png', first), sheet('real-contact-drain-selected12.png', contact)]
    put(OUT / 'selected-images.json', dict(
        sheets=sheets, placements=27, unique_image_files=len({str(f) for f in first + contact}),
        everyframe_visual_claim=False, screenshot_scope='Selected complete actual256x240 PPU images, no authored/cropped replacement art'))
    print(json.dumps(dict(passed=True, native_passed=True, output=str(OUT),
                          component_sha256=sha(OUT / 'component-evidence.json')), indent=2))


def freeze():
    ready = verify_ready()
    review = read(OUT / 'agent-visual-review.json')
    assert review['reviewed_selected_whole_images'] is True and review['everyframe_claim'] is False
    assert read(OUT / 'component-evidence.json')['passed'] is True
    assert not (OUT / 'proof.json').exists()
    bindings = dict(ready['bindings'])
    for f in P.rglob('*'):
        if f.is_file():
            bindings[str(f)] = sha(f)
    for f in [Path(__file__), ROOT / 'docs/qa/mario-flower731-east-native-2026-10-26.txt']:
        bindings[str(f)] = sha(f)
    for path, h in bindings.items():
        assert sha(path) == h, path
    put(OUT / 'proof.json', dict(passed=True, ROM_sha256=ROM, native_launches=1, retries=0,
        native_worker_released=True, settings_unchanged=True,
        original_readiness_sha256=READY, original_preparation_binding_count=3145,
        component_evidence_sha256=sha(OUT / 'component-evidence.json'),
        visual_review_sha256=sha(OUT / 'agent-visual-review.json'),
        bindings=bindings, fullroute_allitems_Hard_claim=False))
    print(json.dumps(dict(passed=True, bindings=len(bindings), proof_sha256=sha(OUT / 'proof.json')), indent=2))


def public_checkpoint():
    """Metadata/tools/sample images only; no ROM/audio/settings/capture payload."""
    q = read(OUT / 'proof.json')
    assert q['passed'] and q['ROM_sha256'] == ROM and q['native_launches'] == 1
    for f, h in q['bindings'].items():
        assert sha(f) == h, f
    target = ROOT / 'docs/qa/checkpoints/2026-10-26/mario-physical-flower731-v1'
    target.mkdir(parents=True, exist_ok=False)
    files = []
    def copy(src, name, role):
        assert src.suffix.lower() in ['.py', '.lua', '.json', '.txt', '.png', '.diff']
        assert src.name.lower() != 'settings.json'
        dst = target / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        files.append(dict(path=name, sha256=sha(dst), bytes=dst.stat().st_size,
                          role=role, original_path=str(src), original_sha256=sha(src)))
    for src, name, role in [
        (OUT / 'proof.json', 'native/proof.json', 'Exact731 native/source/environment/tool result bindings'),
        (P / 'native-proof.json', 'native/native-proof.json', 'Fresh one-run native endpoint and component result'),
        (N / 'native-receipt.json', 'native/native-receipt.json', 'Actual731 exit0/no-retry/CHR component receipt'),
        (OUT / 'component-evidence.json', 'native/component-evidence.json', 'Independent saved-data pickup/growth/contact/drain derivation'),
        (OUT / 'agent-visual-review.json', 'native/agent-visual-review.json', 'Actual selected-image review with explicit limits'),
        (OUT / 'selected-images.json', 'native/selected-images.json', 'Whole-PPU source-image hashes for two sample sheets'),
        (OUT / 'fresh731-versus-historical900.json', 'comparison/fresh731-versus-historical900.json', 'Twelve actualCSV comparisons; no result transfer'),
        (P / 'metadata-rebind-only.diff', 'source/metadata-rebind-only.diff', 'Exact900-to731 genuine metadata/path rebind; controls unchanged'),
        (P / 'actual731-source-configuration.json', 'source/actual731-source-configuration.json', 'Actual731 PCs/banks/opcodes/RAM/SFX/GameLoop-RTS metadata'),
        (P / 'freeze-v1/receipt.json', 'source/preparation-freeze.json', 'Pre-run source-only readiness receipt'),
        (P / 'source-controls-v1/proof.json', 'source/assembled-component-controls.json', 'Fresh731 ten assembled components and authored real block bytes'),
        (P / 'startup-static-v1/proof.json', 'source/static-startup-controls.json', '439 mocked startup frames and fixed CHR observer equivalence'),
        (P / 'controller-source-controls-v1/proof.json', 'source/right-controller-controls.json', '81 source returns/wait bound/five unsafe controls'),
        (P / 'east-source-controls-v1/proof.json', 'source/east-controller-controls.json', 'Unchanged East/B pulse and original gap/enemy policy mocks')]:
        copy(src, name, role)
    for name in ['mario_flower731_prepare_v1.py', 'mario_flower731_result_v1.py',
                 'mario_flower900_native_v4.lua', 'mario_flower900_run_v1.py']:
        copy(ROOT / 'tools/audit' / name, 'frozen-tools/' + name, 'Exact preparation/result or reused passing observer/one-shot runner')
    for name in ['mario-flower731-east-preparation-2026-10-26.txt', 'mario-flower731-east-native-2026-10-26.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name, 'Exact731 preparation or native result and coverage limits')
    for name in ['physical-progression-selected15.png', 'real-contact-drain-selected12.png']:
        copy(OUT / name, 'image-samples/' + name, 'Inspected selected complete actual731 PPU images')
    readme = '''Installed clean731 MarioEasy physical Fire progression: PASS

Exact731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c.
ONE fresh granted native launch,0retries,0deaths,1945frame endpoint. Worker
released. Real336/1248blocks, pickups839/1457,60+60source growth updates,
retainedFire2, actual liveGoomba contact1898,46neutralpolls and both projectile
slots cleared by1911. Original45drain and all semanticguards remain.

CHR1396observed frames/0bad; motion1476checks/maxworld-camera3.20raw shot
allocation writes form10frame-slot groups, not20distinct shots.9brick-handler
admissions are not9destroyed bricks. Queue stores are not audible-cue counts.

27selected complete actualPPUimages plus original1904 reviewed. No obvious
block displacement/scenery corruption/missing body part in those samples;
not every captured frame was reviewed. No waveform/source-art/fullDMA/stack/
fiveSMC/allitems/Hard/Luigi/fullroute certification follows.

Fresh731 controller, actual hooks and source configuration are separately
bound. Twelve CSV outputs also match the independently executed900 run, but
no900result is retagged. The900threeFALSE attempts and success remain in the
separate mario-physical-flower900-v1 checkpoint unchanged.

Review-files.json maps every copied file to its exact original/hash/role.
This public checkpoint copies no ROM/NSF/DMC/settings/audio/video/lossless
telemetry payload and launches no emulator. No game/installed/settings/Git
mutation occurs here. Complete original observations remain external.
'''
    (target / 'README.txt').write_text(readme, encoding='utf-8')
    files.append(dict(path='README.txt', sha256=sha(target / 'README.txt'), bytes=(target / 'README.txt').stat().st_size,
                      role='Review entry point and exact finite coverage'))
    manifest = dict(passed=True, review_checkpoint_only=True, ROM_sha256=ROM,
                    copied_ROM_audio_settings_lossless_payload=False, native_launches_by_checkpoint=0,
                    files=files, total_bytes=sum(f['bytes'] for f in files))
    (target / 'review-files.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for r in files:
        assert sha(target / r['path']) == r['sha256'] == r.get('original_sha256', r['sha256'])
    print(json.dumps(dict(passed=True, output=str(target), files=len(files), bytes=manifest['total_bytes'],
                          review_map_sha256=sha(target / 'review-files.json')), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze', action='store_true')
    p.add_argument('--public-checkpoint', action='store_true')
    args = p.parse_args()
    public_checkpoint() if args.public_checkpoint else (freeze() if args.freeze else analyze())
