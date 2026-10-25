"""Bind the six frozen84 native ability receipts; never launches an emulator."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import math
from PIL import Image, ImageDraw
import numpy as np

ROM84 = '84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def picture(path):
    raw = path.read_bytes()
    assert len(raw) == 256 * 240 * 4
    v = np.frombuffer(raw, dtype='<u4').reshape(240, 256)
    return Image.fromarray(np.stack(((v >> 16) & 255, (v >> 8) & 255,
                                    v & 255), axis=2).astype(np.uint8))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    runs, unique = [], {}
    for family, expected in [('pit', 10), ('rygar', 12), ('scrooge', 9)]:
        for mode in ['easy', 'hard']:
            folder = a.root / f'{family}-{mode}-native-v2'
            z = read(folder / 'proof.json')
            n = z['native']
            assert z['passed'] and z['emulator_exit'] == 0 and n['passed']
            assert z['ROM_sha256'] == ROM84 == sha(folder / 'candidate.nes')
            assert z['family'] == family and z['mode'] == mode
            assert len(n['abilities']) == expected
            assert [(x['before'], x['after'], x['transformCalls'])
                    for x in n['physical_collections']] == [(0, 1, 60), (1, 2, 60)]
            for x in n['physical_collections']:
                assert x['headBlockObserved']
                assert x['staged'] < x['revealed'] < x['mature'] < x['collisionPlaced'] <= x['collected']
                assert x['ownerCalls'] == x['beginCalls'] == 1
            assert [x['q'] for x in n['abilities']] == z['abilities']
            for x in n['abilities']:
                assert x['tier'] == x['q']['tier']
                assert x['origin'] == ('cold baseline' if x['tier'] == 0 else f"physical collection {x['tier']}")
                assert x['gameUpdates'] == x['q']['limit']
                kind = x['q']['kind']
                if kind in ['hammer', 'disk_hit', 'pogo_enemy']:
                    assert x['hits'] == x['defeats'] == x['damageCalls'] == 1
                if kind.startswith('disk_'):
                    maximum = x['q']['reach']
                    sequence = list(range(24, maximum + 1, 4)) + list(range(maximum - 4, 19, -4))
                    assert x['caught'] and x['samples'] == sequence
                elif kind == 'flight_full':
                    assert x['burn'] == 60 and x['minFuel'] == 0 and x['exhausted'] and x['recharged'] and x['relaunched']
                elif kind == 'flight_release':
                    assert x['burn'] == 19 and x['minFuel'] == 41 and x['releaseSeen'] and x['recharged']
                elif kind == 'flight_gate':
                    assert x['burn'] == 0 and x['secondAirAttempt'] and not x['flightSeen']
                elif kind == 'pogo_ground':
                    assert x['bounces'] == 3 and x['cancelSeen']
                elif kind == 'pogo_enemy':
                    assert x['bounces'] == 1 and x['cancelSeen']
            hashes = {name: sha(folder / name) for name in [
                'proof.json', 'native-abilities.json', 'preparation.json', 'config.json',
                'run.lua', 'events.jsonl', 'apu.csv', 'ability-updates.csv',
                'final_item_matrix_progressive.lua', 'final_item_abilities_native.lua',
                'final_item_abilities_failure.lua', 'candidate.nes', 'candidate.dbg',
                'candidate.lbl', 'candidate.map', 'host.log']}
            assert hashes['run.lua'] == z['script_sha256']
            assert hashes['final_item_matrix_progressive.lua'] == z['base_fixture_sha256']
            assert hashes['final_item_abilities_native.lua'] == z['ability_module_sha256']
            assert hashes['final_item_abilities_failure.lua'] == z['failure_guard_sha256']
            events = [json.loads(s) for s in (folder / 'events.jsonl').read_text().splitlines()]
            counts = Counter(e['kind'] for e in events)
            assert counts['ability-started'] == counts['ability-completed'] == expected
            captured = [e for e in events if e['kind'] == 'ppu-frame-captured']
            assert len(captured) == len(list(folder.glob('*.argb')))
            captures = []
            for e in captured:
                path = folder / (e['data']['name'] + '.argb')
                h = sha(path)
                if h not in unique:
                    image = picture(path)
                    destination = a.output / f'frame-{len(unique)+1:03}.png'
                    image.save(destination)
                    unique[h] = dict(id=len(unique)+1, raw_sha256=h, png=str(destination),
                                     png_sha256=sha(destination), image=image, aliases=[])
                u = unique[h]
                alias = dict(run=folder.name, name=e['data']['name'], event=e)
                u['aliases'].append(alias)
                captures.append(dict(raw=str(path), sha256=h, unique_frame=u['id'], event=e))
            runs.append(dict(family=family, mode=mode, folder=str(folder), hashes=hashes,
                             proof=z, event_counts=dict(counts), captures=captures))
    assert len({r['proof']['runner_sha256'] for r in runs}) == 1
    assert len({r['proof']['ability_module_sha256'] for r in runs}) == 1
    sheets = []
    frames = list(unique.values())
    for start in range(0, len(frames), 20):
        page = frames[start:start+20]
        sheet = Image.new('RGB', (256*5, 270*math.ceil(len(page)/5)), (20, 25, 32))
        draw = ImageDraw.Draw(sheet)
        for i, u in enumerate(page):
            x, y = (i % 5)*256, (i//5)*270
            sheet.paste(u['image'], (x, y+30))
            q = u['aliases'][0]
            draw.text((x+2, y+1), f"{u['id']:03} {q['run'].replace('-native-v2','')}", fill='white')
            draw.text((x+2, y+15), q['name'], fill='white')
        path = a.output / f'unique-frames-{start//20+1:02}.png'
        sheet.save(path)
        sheets.append(dict(path=str(path), sha256=sha(path), first=start+1, last=start+len(page)))
    for u in unique.values():
        del u['image']
    failure = a.root / 'scrooge-easy-native-v1'
    controls = a.root / 'source-controls-v1/enemy-standing-control.json'
    assert not read(failure / 'proof.json')['passed']
    rejected = dict(folder=str(failure), classification='fixture_error_not_game_defect',
                    first_failure=read(failure / 'first-failure.json'),
                    hashes={f: sha(failure/f) for f in ['proof.json', 'first-failure.json',
                        'first-failure.argb', 'events.jsonl', 'ability-updates.csv', 'run.lua']},
                    explanation='Initial Goomba canonicalY192 misses floor208 admission, becomes falling state1; corrected canonicalY184 and raised168 are admitted by original enemy-floor owner. No gameplay assertion removed.',
                    source_control=str(controls), source_control_sha256=sha(controls),
                    source_control_result=read(controls))
    totals = {name: sum(r['proof']['native'][field] for r in runs) for name, field in [
        ('game_updates', 'updates'), ('nmis', 'nmis'), ('irq_scroll_stores', 'irq_scroll_stores'),
        ('hardware_chr_checks', 'hardware_chr_checks'), ('complete_dma_checks', 'complete_dma_checks'),
        ('apu_writes', 'apuWrites')]}
    summary = dict(passed=True, goal_complete=False, ROM_sha256=ROM84, native_runs=6,
                   distinct_identities=3, mode_cells=6, ability_cases=62,
                   physical_collections=12, committed_transform_updates=720,
                   **totals, minimum_sampled_sp=min(r['proof']['native']['minSP'] for r in runs),
                   raw_ppu_captures=sum(len(r['captures']) for r in runs),
                   unique_raw_ppu_frames=len(unique), runs=runs,
                   frame_manifest=frames, sheets=sheets, retained_failure=rejected,
                   limits=[
                       'Bounded same-page dry stationary-player arenas; visible/logical world and Goomba default-health targets explicitly staged.',
                       'Actual A head reveal/native full rise; actor contact explicitly placed only after maturity. No tier/inventory/fuel/flight/reach/pogo injection.',
                       'Two real acquisitions per run, then exact owner/input/cleanup checks. Three identities in six mode cells, not 62 identities or 12 new identity counts.',
                       'Native OAM/CHR/IRQ guards and APU writes are not exhaustive original-pixel, waveform-fidelity, campaign or sustained-performance qualification.',
                       'Scrooge tests one-hit Goomba defeat/rebound; durable-target body-contact priority, immunities and simultaneous targets remain untested here.',
                       'Pit roof/water/Down/death cancellation and Rygar crouch/movement/page-edge/multiple-target cases remain outside this batch.',
                       'Full roster, every item, every form and full goal remain open.'])
    output = a.output / 'proof.json'
    output.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in [
        'runs', 'frame_manifest', 'sheets', 'retained_failure', 'limits']}))
    print(json.dumps(dict(proof=str(output), sha256=sha(output), sheets=sheets)))


if __name__ == '__main__':
    main()
