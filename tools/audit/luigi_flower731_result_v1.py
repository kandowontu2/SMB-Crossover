"""Analyze/freeze the single corrected Rg-owner Luigi731 result; no native runs."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'luigi-flower731-rg-owner-v1'
N = P / 'luigi-easy'
OUT = P / 'native-result-freeze-v1'
READY = 'b443734f84719a0022936a1aff749275e7c76aa8ee72ccb01ad45ff1d0ab9697'
SHA = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())
def put(p, z):
    assert not p.exists(), p
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')
def rows(name):
    with (N / name).open() as f:return list(csv.DictReader(f))
def verify():
    assert sha(P / 'readiness.json') == READY
    r = get(P / 'readiness.json')
    assert len(r['bindings']) == 3964
    for p, h in r['bindings'].items():assert sha(p) == h, p
    return r


def analyze():
    verify();OUT.mkdir(exist_ok=False)
    native = get(P / 'native-proof.json')
    assert native['passed'] and native['native_worker_released'] and native['profiles_run'] == 1
    r = native['profiles'][0]
    assert r['passed'] and r['exit'] == 0 and r['retries'] == 0 and r['result']['frames'] == 2054 and r['result']['deaths'] == 0
    c = r['component']
    assert c['ROM_sha256'] == SHA and c['character'] == 8 and c['variant'] == 1 and c['actual_mode'] == 0
    assert c['pool_inactive'] and c['shots'] == c['source_fire_requests'] == 8 and c['enemy_contacts'] == 1
    owners = [json.loads(s) for s in (N / 'flower-owner.jsonl').read_text().splitlines()]
    pickups = [r for r in owners if r['kind'] == 'real-native-collection']
    assert [(r['frame'], r['type'], r['slot']) for r in pickups] == [(851, 0, 5), (1653, 1, 5)]
    state = {int(r['frame']): r for r in rows('flower-state.csv')}
    growth = []
    for first, last, xy, item in [(852, 911, ('408', '176'), '1'), (1654, 1713, ('1260', '111'), '2')]:
        z = [state[f] for f in range(first, last + 1)]
        assert all((r['x'], r['y']) == xy and r['growing'] == '1' and r['collected'] == item for r in z)
        assert [int(r['age']) for r in z] == list(range(60))
        growth.append(dict(first=first, last=last, source_updates=60, held_position=xy))
    assert all(state[f]['power'] == '2' and state[f]['growing'] == '0' for f in range(1714, 2055))
    alloc = [r for r in owners if r['kind'] == 'actual-rg-allocation']
    requests = [r for r in owners if r['kind'] == 'actual-rg-fire-request']
    contacts = [r for r in owners if r['kind'] == 'actual-rg-enemy-contact']
    assert len(alloc) == len(requests) == 8 and len(contacts) == 1
    assert [(r['frame'], r['slot']) for r in alloc] == [(1761, 9), (1776, 8), (1808, 9), (1824, 8), (1872, 9), (1888, 8), (1969, 9), (1984, 8)]
    assert all(r['value'] == 32 for r in requests)
    assert {k: contacts[0][k] for k in ['frame', 'enemySlot', 'enemyID', 'shotSlot', 'shotType', 'bridgeType', 'state']} == dict(frame=2007, enemySlot=2, enemyID=0, shotSlot=8, shotType=3, bridgeType=30, state=0)
    neutral = [r for r in rows('inputs.csv') if int(r['frame']) >= 2008]
    assert len(neutral) == 46 and all(r['mask'] == '0' for r in neutral)
    assert state[2009]['phase'] == 'drain' and state[2017]['rgLive'] == '0'
    assert all(state[f]['rgLive'] == '0' and state[f]['rgTypes'] == '' for f in range(2017, 2055))
    assert max(int(r['rgLive']) for r in state.values()) == 2
    chrrows = rows('chr-commit.csv')
    assert len(chrrows) == 1516 and not any(int(r['bad']) for r in chrrows)
    motion = get(N / 'completed-loop-motion.json')
    assert motion == dict(passed=True, checks=1535, max_world_step=3, max_camera_step=3, game_state_writes=False)
    assert {r['lives'] for r in rows('trace.csv') if int(r['frame']) >= 371} == {'2'}
    put(OUT / 'component-evidence.json', dict(passed=True, ROM_sha256=SHA, native_launches=1, retries=0, native_worker_released=True,
        actual_character=8, actual_variant=1, actual_mode=0, genuine_pickups=pickups, growth=growth,
        genuine_allocations=alloc, genuine_source_fire_requests=requests, actual_live_green_Koopa_contact=contacts[0],
        source_store_request_count=8, raw_queue_fire_request_stores=16,
        sound_scope='Eight actual original source STA requests plus16raw queue stores, not audible/waveform parity.',
        neutral_polls=46, original_minimum_drain=45, actual_ten_slot_pool_empty_from2017=True,
        observed_maximum_active_slots=2, final_power=2, endpoint_frame=2054, CHR=r['CHR'], motion=motion,
        wrong_owner_native_FALSE_not_rewritten=True, scope='Fresh731 LuigiEasy physical mushroom/flower progression and original Rg3 contact/drain only; not Hard/allitems/fullroute/source-art/waveform certification.'))
    images = [N / 'frames/000704.png', N / 'growth-1-852.png', N / 'growth-1-911.png',
              N / 'frames/001568.png', N / 'frames/001616.png', N / 'frames/001648.png',
              N / 'growth-2-1654.png', N / 'growth-2-1684.png', N / 'growth-2-1713.png',
              N / 'frames/001768.png', N / 'frames/001984.png', N / 'frames/002000.png',
              N / 'frames/002008.png', N / 'frames/002016.png', N / 'frames/002024.png',
              N / 'frames/002048.png', N / 'endpoint.png']
    sheets = []
    for group, name in [(images[:9], 'physical-pickups-growth-selected9.png'), (images[9:], 'genuine-Rg-contact-drain-selected8.png')]:
        sheet = Image.new('RGB', (1536, ((len(group) + 2) // 3) * 528), '#172132');draw = ImageDraw.Draw(sheet)
        for i, p in enumerate(group):
            im = Image.open(p).convert('RGB');assert im.size == (256, 240)
            x, y = i % 3 * 512, i // 3 * 528;draw.text((x + 8, y + 8), p.name, fill='white')
            sheet.paste(im.resize((512, 480), Image.Resampling.NEAREST), (x, y + 36))
        sheet.save(OUT / name);sheets.append(dict(path=str(OUT / name), sha256=sha(OUT / name)))
    put(OUT / 'selected-images.json', dict(placements=17, everyframe_visual_claim=False, sheets=sheets,
        images=[dict(path=str(f), sha256=sha(f)) for f in images]))
    print(json.dumps(dict(passed=True, native_passed=True, component_sha256=sha(OUT / 'component-evidence.json')), indent=2))


def freeze():
    r = verify();v = get(OUT / 'agent-visual-review.json')
    assert v['reviewed_selected_whole_images'] and not v['everyframe_claim']
    assert get(OUT / 'component-evidence.json')['passed']
    bindings = dict(r['bindings'])
    for f in P.rglob('*'):
        if f.is_file():bindings[str(f)] = sha(f)
    for f in [Path(__file__), ROOT / 'docs/qa/luigi-flower731-Rg-native-2026-10-26.txt']:bindings[str(f)] = sha(f)
    for f, h in bindings.items():assert sha(f) == h, f
    put(OUT / 'proof.json', dict(passed=True, ROM_sha256=SHA, native_launches=1, retries=0, native_worker_released=True,
        original_readiness_sha256=READY, preparation_bindings_reverified=3964, bindings=bindings,
        prior_wrong_owner_FALSE_preserved=True, Hard_allitems_fullroute_waveform_claim=False))
    print(json.dumps(dict(passed=True, bindings=len(bindings), proof_sha256=sha(OUT / 'proof.json')), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze', action='store_true');a = p.parse_args()
    freeze() if a.freeze else analyze()
