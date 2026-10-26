"""Independently freeze two exact641 physical Luigi results; never launches Mesen."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'luigi-profile641-native-ready-v2'
S = D / 'luigi-mario-profile731-v3'
OUT = P / 'native-result-freeze-v1'
ROM = '641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
READY = 'a7cea8eac398ec7fb8df294fad7d6d6ed49c2677285414092f9e2329d7d3a21c'
SOURCE = '518556a39e0045bca8edebf5298420d0fc8ca6ee236d5eacf0b95dfcf55f2680'
ROOT_REVIEW = D / 'root-luigi641-build-v1/ROOT-review.json'
ROOT_REVIEW_SHA = 'e7dd02d246672c49aa96bc8d59f1b6b351836d66741d76132c46b0c19134389a'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())
def put(p, z):
    assert not p.exists(), p
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')
def rows(n, name):
    with (n / name).open() as f:return list(csv.DictReader(f))
def verify():
    bindings = {}
    for p, h, count in [(P / 'readiness.json', READY, 5323),
                         (S / 'source-ready-v1/readiness.json', SOURCE, 1824),
                         (P / 'freeze-v1/receipt.json', 'f71bd0cb70345613d45409f6cd07ed699327dfc7e9ebc02e5bff070a3ffa078f', 5)]:
        assert sha(p) == h, p
        r = get(p);b = r.get('bindings', r.get('additional_bindings'));assert len(b) == count
        for f, expected in b.items():assert sha(f) == expected, f
        bindings.update(b);bindings[str(p)] = h
    assert sha(ROOT_REVIEW) == ROOT_REVIEW_SHA
    bindings[str(ROOT_REVIEW)] = ROOT_REVIEW_SHA
    return bindings


def analyze():
    verify();OUT.mkdir(exist_ok=False)
    native = get(P / 'native-proof.json')
    assert native['passed'] and native['native_worker_released'] and native['profiles_run'] == 2 and native['retries'] == 0
    expected = [dict(name='luigi-easy', mode=0, frames=1958, stage=371, reveal=[719, 1378],
                     pickup=[867, 1494], position=[['413', '176'], ['1260', '99']],
                     growth=[868, 1495], shots=13, contacts=[(1911, 2, 0, 9)], empty=1912,
                     chr=1379, body=1309, motion=1430, finalx='1636', launch=1462,
                     image_frames=[712, 736, 856, 936, 1368, 1400, 1464, 1488, 1560, 1576, 1904, 1912, 1920, 1952]),
                dict(name='luigi-hard', mode=1, frames=2105, stage=458, reveal=[810, 1462],
                     pickup=[959, 1579], position=[['413', '176'], ['1259', '111']],
                     growth=[960, 1580], shots=15, contacts=[(2058, 0, 6, 8), (2077, 1, 6, 9)], empty=2078,
                     chr=1443, body=1337, motion=1471, finalx='1745', launch=1544,
                     image_frames=[808, 832, 952, 1024, 1456, 1480, 1544, 1576, 1640, 1656, 2056, 2064, 2080, 2104])]
    evidence = [];image_manifest = []
    for q, result in zip(expected, native['profiles']):
        n = P / q['name'];c = result['component'];r = result['result']
        assert result['name'] == q['name'] and result['passed'] and result['exit'] == result['retries'] == 0
        assert r['frames'] == q['frames'] and r['polls'] == q['frames'] - 1 and r['deaths'] == 0
        assert r['stage_entries'] == {'0-0': q['stage']}
        assert c['ROM_sha256'] == ROM and c['actual_mode'] == q['mode'] and c['character'] == 8 and c['variant'] == 1
        assert c['passed'] and c['pool_inactive'] and c['no_fixture_game_state_writes']
        assert c['shots'] == c['source_fire_requests'] == q['shots'] and c['enemy_contacts'] == len(q['contacts'])
        owners = [json.loads(s) for s in (n / 'flower-owner.jsonl').read_text().splitlines()]
        pickups = [s for s in owners if s['kind'] == 'real-native-collection']
        reveals = [s for s in owners if s['kind'] == 'real-block-reveal']
        assert [s['frame'] for s in reveals] == q['reveal'] and [s['blockX'] for s in reveals] == [336, 1248]
        assert [(s['frame'], s['type'], s['slot'], s['playerPower']) for s in pickups] == [(q['pickup'][0], 0, 5, 0), (q['pickup'][1], 1, 5, 1)]
        state = {int(s['frame']): s for s in rows(n, 'flower-state.csv')}
        growth = []
        for i, first in enumerate(q['growth']):
            z = [state[f] for f in range(first, first + 60)]
            assert all([s['x'], s['y']] == q['position'][i] and s['growing'] == '1' and s['collected'] == str(i + 1) and s['engine'] == '9' for s in z)
            assert [int(s['age']) for s in z] == list(range(60))
            assert all(s['power'] == str(i) for s in z)
            growth.append(dict(first=first, last=first + 59, source_updates=60, held_position=q['position'][i]))
        assert all(state[f]['power'] == '2' and state[f]['growing'] == '0' for f in range(q['growth'][1] + 60, q['frames'] + 1))
        alloc = [s for s in owners if s['kind'] == 'actual-rg-allocation']
        requests = [s for s in owners if s['kind'] == 'actual-rg-fire-request']
        contacts = [s for s in owners if s['kind'] == 'actual-rg-enemy-contact']
        assert len(alloc) == len(requests) == q['shots'] and all(s['value'] == 32 for s in requests)
        assert [(s['frame'], s['enemySlot'], s['enemyID'], s['shotSlot']) for s in contacts] == q['contacts']
        assert all(s['shotType'] == 3 and s['bridgeType'] == 30 and s['state'] == 0 for s in contacts)
        first_contact = contacts[0]['frame']
        neutral = [s for s in rows(n, 'inputs.csv') if int(s['frame']) > first_contact]
        assert len(neutral) == 46 and all(s['mask'] == '0' for s in neutral)
        assert all(state[f]['rgLive'] == '0' and state[f]['rgTypes'] == '' for f in range(q['empty'], q['frames'] + 1))
        assert max(int(s['rgLive']) for s in state.values()) == 2
        assert state[q['frames']]['x'] == q['finalx'] and state[q['frames']]['y'] == '176'
        chrrows = rows(n, 'chr-commit.csv');assert len(chrrows) == q['chr'] and not any(int(s['bad']) for s in chrrows)
        assert result['CHR']['body_constructions'] == q['body']
        motion = get(n / 'completed-loop-motion.json')
        assert motion == dict(passed=True, checks=q['motion'], max_world_step=3, max_camera_step=3, game_state_writes=False)
        assert {s['lives'] for s in rows(n, 'trace.csv') if int(s['frame']) >= q['stage']} == {'2'}
        assert c['fire_request_stores'] == 2 * q['shots'] and c['pickup_request_stores'] == 4 and c['reveal_request_stores'] == 8
        evidence.append(dict(name=q['name'], actual_mode=q['mode'], actual_identity=8, actual_variant=1,
                             physical_frames=q['frames'], deaths=0, genuine_reveals=reveals, genuine_pickups=pickups,
                             growth=growth, final_power=2, actual_allocations=alloc, actual_source_fire_requests=requests,
                             raw_fire_queue_stores=2*q['shots'], actual_live_enemy_contacts=contacts,
                             neutral_polls=46, minimum_drain=45, all_ten_Rg_slots_empty_from=q['empty'],
                             observed_maximum_live_Rg_slots=2, CHR=result['CHR'], motion=motion,
                             Hard_second_contact_during_neutral_is_prior_inflight_projectile=q['mode'] == 1))
        images = [n / 'frames' / f'{f:06d}.png' for f in q['image_frames']]
        images += [n / f'growth-{i+1}-{first+age}.png' for i, first in enumerate(q['growth']) for age in [0, 30, 59]]
        images.append(n / 'endpoint.png')
        sheets = []
        for j in range(0, len(images), 9):
            group = images[j:j+9]
            sheet = Image.new('RGB', (1536, ((len(group) + 2)//3)*528), '#172132');draw = ImageDraw.Draw(sheet)
            for i, p in enumerate(group):
                im = Image.open(p).convert('RGB');assert im.size == (256, 240)
                x, y = i % 3 * 512, i // 3 * 528;draw.text((x+8, y+8), f'{q["name"]} {p.name}', fill='white')
                sheet.paste(im.resize((512, 480), Image.Resampling.NEAREST), (x, y+36))
            dst = OUT / f'{q["name"]}-selected-{j//9+1}.png';sheet.save(dst)
            sheets.append(dict(path=str(dst), sha256=sha(dst)))
        image_manifest.append(dict(profile=q['name'], placements=len(images), sheets=sheets,
                                   images=[dict(path=str(f), sha256=sha(f)) for f in images]))
    put(OUT / 'component-evidence.json', dict(passed=True, adopted=False, ROM_sha256=ROM,
        native_launches=2, retries=0, native_worker_released=True, profiles=evidence,
        sound_scope='Actual original source STA requests and raw queue stores only, not audible/waveform parity.',
        scope='Exact private641 physical Luigi Easy/Hard two-item progression/contact/drain; no full1-1, owned-cadence, E008 full-transfer/enable-timing or adoption claim.'))
    put(OUT / 'selected-images.json', dict(whole_PPU_size=[256, 240], placements=sum(s['placements'] for s in image_manifest),
                                          everyframe_visual_claim=False, profiles=image_manifest))
    print(json.dumps(dict(passed=True, profiles=2, placements=sum(s['placements'] for s in image_manifest)), indent=2))


def freeze():
    bindings = verify();v = get(OUT / 'agent-visual-review.json')
    assert v['reviewed_selected_whole_images'] and not v['everyframe_claim']
    assert get(OUT / 'component-evidence.json')['passed']
    for f in P.rglob('*'):
        if f.is_file():bindings[str(f)] = sha(f)
    for f in [Path(__file__), ROOT / 'docs/qa/luigi-profile641-native-2026-10-26.txt']:bindings[str(f)] = sha(f)
    for f, expected in bindings.items():assert sha(f) == expected, f
    put(OUT / 'proof.json', dict(passed=True, adopted=False, ROM_sha256=ROM, parent_ROM_sha256='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c',
        native_launches=2, retries=0, native_worker_released=True, original_native_readiness_sha256=READY,
        source_readiness_sha256=SOURCE, preparation_source_native_seal_bindings=[1824, 5323, 5],
        ROOT_independent_build_review_sha256=ROOT_REVIEW_SHA, bindings=bindings,
        owned_cadence_full1_1_replay_E008_timing_adoption_claim=False))
    print(json.dumps(dict(passed=True, bindings=len(bindings), proof_sha256=sha(OUT / 'proof.json')), indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze', action='store_true');a=p.parse_args()
    freeze() if a.freeze else analyze()
