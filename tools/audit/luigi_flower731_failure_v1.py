"""Freeze the exact failed Luigi observer attempt and diagnose its wrong projectile owner."""
from pathlib import Path
import csv
import hashlib
import json
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'luigi-flower731-east-ready-v2'
N = P / 'luigi-easy'
OUT = P / 'failure-freeze-v1'
sys.path.insert(0, str(ROOT / 'tools/audit'))
from check_tmnt_render_oa import load
from robots_weapon_cpu_v1 import Arena


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, z):
    assert not p.exists(), p
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(exist_ok=False)
    assert sha(P / 'readiness.json') == '439dac1cf1525669efe2e6d14bf89d9c2c30fed9555e9679dc2534c74b97813f'
    ready = json.loads((P / 'readiness.json').read_text())
    for p, h in ready['bindings'].items():
        assert sha(p) == h, p
    native = json.loads((P / 'native-proof.json').read_text())
    assert native['passed'] is False and native['native_worker_released']
    assert native['profiles_run'] == 1 and native['profiles'][0]['retries'] == 0
    assert 'Bounded actual fireball use and release' in (N / 'candidate-run.log').read_text()
    assert not (N / 'flower-component.json').exists() and not (N / 'chr-commit.json').exists()
    owners = [json.loads(s) for s in (N / 'flower-owner.jsonl').read_text().splitlines()]
    pickups = [s for s in owners if s['kind'] == 'real-native-collection']
    assert [(s['frame'], s['type'], s['slot']) for s in pickups] == [(851, 0, 5), (1653, 1, 5)]
    with (N / 'flower-state.csv').open() as f:
        state = {int(r['frame']): r for r in csv.DictReader(f)}
    growth = []
    for first, last, xy, item in [(852, 911, ('408', '176'), '1'), (1654, 1713, ('1260', '111'), '2')]:
        rows = [state[f] for f in range(first, last + 1)]
        assert all((r['x'], r['y']) == xy and r['growing'] == '1' and r['collected'] == item for r in rows)
        assert [int(r['age']) for r in rows] == list(range(60))
        growth.append(dict(first=first, last=last, source_updates=60, held_position=xy))
    assert all(state[f]['power'] == '2' and state[f]['growing'] == '0' for f in range(1714, 2261))
    assert all(state[f]['shot0'] == '0' and state[f]['shot1'] == '0' for f in range(1761, 2261))
    assert not any(r['kind'].startswith('actual-fireball-') for r in owners)
    with (N / 'render.csv').open() as f:
        render = list(csv.DictReader(f))
    shooting = [r for r in render if int(r['frame']) >= 1761 and int(r['shoot']) > 0]
    assert shooting
    with (N / 'trace.csv').open() as f:
        trace = list(csv.DictReader(f))
    assert {r['lives'] for r in trace if int(r['frame']) >= 371} == {'2'}
    with (N / 'chr-commit.csv').open() as f:
        chrrows = list(csv.DictReader(f))
    assert len(chrrows) == 1722 and not any(int(r['bad']) for r in chrrows)
    rom = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes'
    b = load(rom)
    source_cases = []
    for power, held, previous in [(1, 64, 0), (2, 0, 0), (2, 64, 64), (2, 64, 0)]:
        q = Arena(b, char=8)
        q.put(CrossoverBehaviorVersion=0, MarioVariant=1, PlayerStatus=power, PlayerSize=0,
              Player_State=0, RgCrouch=0, RgPreviousButtons=previous, SavedJoypadBits=held,
              A_B_Buttons=held, PreviousA_B_Buttons=previous, TimerControl=0)
        q.invoke('ProcFireball_Bubble')
        pool = [q.get('RgShotType', i) for i in range(10)]
        expected = power == 2 and held == 64 and previous == 0
        assert sum(v == 3 for v in pool) == int(expected) and all(v in [0, 3] for v in pool)
        assert [q.get('Fireball_State', i) for i in range(2)] == [0, 0]
        source_cases.append(dict(power=power, held=held, previous=previous, RgShotType=pool,
                                 Fireball_State=[0, 0], actual_owner='ProcFireball_Bubble -> RlWeaponsDispatch -> ExpandedWeapons',
                                 source_only=True))
    put(OUT / 'component-evidence.json', dict(analysis_passed=True, native_passed=False,
        ROM_sha256=ready['ROM_sha256'], native_launches=1, retries=0, native_worker_released=True,
        genuine_pickups=pickups, growth=growth, retained_Fire1714_through2260=True,
        first_observed_Rg_shoot_pose_frame=int(shooting[0]['frame']), native_Mario_slot_allocations_observed=0,
        projectile_owner_diagnosis='The fixture watched Mario Fireball_State/native enemy-hit hook. Luigi8 dispatches ExpandedWeapons, clears Mario slots and uses RgShotType3 in ten shared slots with a two-shot limit. Native allocation/contact/drain were unobserved, not proven absent.',
        actual_complete_dispatcher_source_controls=source_cases,
        partial_CHR_rows=1722, partial_CHR_bad=0,
        original_motion_final_JSON=json.loads((N / 'completed-loop-motion.json').read_text()),
        no_final_successful_component_or_CHR_receipt=True, no_retry_or_game_change=True,
        scope='Two physical pickups/120growth and selected visible Luigi shots are components of an overall FALSE observer attempt. No actual Rg allocation/contact/lifetime/SFX waveform or fullroute qualification.'))
    selected = [N / 'frames/000704.png', N / 'growth-1-852.png', N / 'growth-1-911.png',
                N / 'frames/001496.png', N / 'frames/001568.png', N / 'frames/001616.png',
                N / 'frames/001648.png', N / 'growth-2-1654.png', N / 'growth-2-1713.png',
                N / 'frames/001768.png', N / 'frames/001816.png', N / 'frames/001888.png',
                N / 'frames/001944.png', N / 'frames/002072.png', N / 'frames/002184.png',
                N / 'frames/002256.png']
    sheets = []
    for group, name in [(selected[:9], 'physical-progression-selected9.png'), (selected[9:], 'visible-Rg-shots-selected7.png')]:
        sheet = Image.new('RGB', (1536, ((len(group) + 2) // 3) * 528), '#172132')
        d = ImageDraw.Draw(sheet)
        for i, p in enumerate(group):
            im = Image.open(p).convert('RGB');assert im.size == (256, 240)
            x, y = i % 3 * 512, i // 3 * 528
            d.text((x + 8, y + 8), p.name, fill='white')
            sheet.paste(im.resize((512, 480), Image.Resampling.NEAREST), (x, y + 36))
        sheet.save(OUT / name)
        sheets.append(dict(path=str(OUT / name), sha256=sha(OUT / name)))
    put(OUT / 'selected-images.json', dict(placements=16, everyframe_visual_claim=False, sheets=sheets,
        images=[dict(path=str(f), sha256=sha(f)) for f in selected]))
    print(json.dumps(dict(analysis_passed=True, native_passed=False, output=str(OUT),
                          component_sha256=sha(OUT / 'component-evidence.json')), indent=2))


if __name__ == '__main__':
    main()
