"""Compare independent mechanics arenas with pinned, pre-rewrite Mario."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('x', 'y', 'yHigh', 'state', 'vx', 'xFraction', 'vy', 'yForce',
          'gravity', 'fallGravity', 'brakeLow', 'brakeHigh', 'size', 'crouch',
          'engine', 'qvx0', 'qvx1', 'qvx2', 'qvy0', 'qvy1', 'qvy2', 'spring',
          'body')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def grouped(rows):
    result = {}
    for row in rows:
        result.setdefault((row['action'], int(row['power'])), []).append(row)
    return result


def review_death(path: Path, character: int):
    meta = json.loads((ROOT / 'tests/mario-native-death-reference.json').read_text())
    packed = (ROOT / 'tests/mario-native-death-reference.csv.gz').read_bytes()
    assert sha(packed) == meta['trace_gzip_sha256'], 'Pinned native death control'
    assert sha((ROOT / 'tests/native-brother-death.lua').read_bytes()) == meta['controller_fixture_sha256'], 'Native death fixture matches independent control'
    raw = gzip.decompress(packed)
    assert sha(raw) == meta['trace_sha256']
    reference = list(csv.DictReader(io.StringIO(raw.decode())))
    rows = list(csv.DictReader(io.StringIO(path.read_text())))
    assert len(rows) == len(reference) == meta['rows'], 'Native death/life-loss duration matches Mario'
    for a, b in zip(reference, rows):
        assert a == b, f'Native death physics differs at age{a["age"]}: {[f for f in a if a[f] != b[f]]}'
    return dict(character=character, result='passed', control_checkpoint=meta['checkpoint'],
                identical_death_rows=len(rows), final_age=int(rows[-1]['age']))


def review_water_pit(path: Path, character: int):
    meta = json.loads((ROOT / 'tests/mario-native-water-pit-reference.json').read_text())
    packed = (ROOT / 'tests/mario-native-water-pit-reference.csv.gz').read_bytes()
    assert sha(packed) == meta['trace_gzip_sha256']
    assert sha((ROOT / 'tests/native-brother-water-pit.lua').read_bytes()) == meta['controller_fixture_sha256']
    raw = gzip.decompress(packed)
    assert sha(raw) == meta['trace_sha256']
    reference = list(csv.DictReader(io.StringIO(raw.decode())))
    rows = list(csv.DictReader(io.StringIO(path.read_text())))
    count = meta['identical_fall_and_life_rows']
    assert rows[:count] == reference[:count], 'The entire native water fall and life deduction match Mario'
    extra = meta['luigi_lives_screen_extra_frames'] if character == 8 else 0
    assert len(rows) == meta['mario_respawn_frames'] + extra, 'Bounded measured room/lives-screen initialization'
    assert rows[-1]['engine'] == '8' and rows[-1]['lives'] == '1', 'The same character respawns playable'
    return dict(character=character, result='passed', identical_fall_and_life_rows=count,
                respawn_frames=len(rows), additional_lives_screen_frames=extra)


def review(path: Path, character: int):
    meta = json.loads((ROOT / 'tests/mario-native-physics-reference.json').read_text())
    packed = (ROOT / 'tests/mario-native-physics-reference.csv.gz').read_bytes()
    assert sha(packed) == meta['trace_gzip_sha256'], 'Pinned Mario reference bytes'
    assert sha((ROOT / 'tests/native-brothers-physics.lua').read_bytes()) == meta['controller_fixture_sha256'], 'Independent fixture still matches the pinned Mario control'
    reference = gzip.decompress(packed)
    assert sha(reference) == meta['trace_sha256'], 'Uncompressed Mario reference'
    old = grouped(csv.DictReader(io.StringIO(reference.decode())))
    new = grouped(csv.DictReader(io.StringIO(path.read_text())))
    assert new.keys() == old.keys() and len(new) == 39, 'All39 trials in all3 power forms'
    for key, rows in new.items():
        assert len(rows) == 128 and [int(r['tick']) for r in rows] == list(range(1, 129)), f'Complete controller trial {key}'

    def equal(key, count=128):
        fields = FIELDS + (('platformContact', 'platformX') if key[0] == 'platform' else ())
        for a, b in zip(old[key][:count], new[key][:count]):
            different = [f for f in fields if a[f] != b[f]]
            assert not different, f'{key}, tick{b["tick"]}: native fields differ: {different}'

    if character == 0:
        for key in old:
            equal(key)
        return dict(character=0, result='passed', control_checkpoint=meta['checkpoint'],
                    identical_trials=39, identical_physics_rows=39 * 128)

    assert character == 8
    metrics = []
    for power in range(3):
        for action in ('crouch', 'water', 'whirlpool', 'vine', 'platform', 'spring'):
            equal((action, power))
        for action in ('walk', 'run'):
            equal((action, power), 48)  # Native acceleration and maximum speeds.

        heights = {}
        for action in ('jump', 'short', 'runjump'):
            key = (action, power)
            first = 32 if action == 'runjump' else 0
            values = []
            for rows in (old[key], new[key]):
                values.append(176 - min((int(r['yHigh']) - 1) * 256 + int(r['y']) for r in rows[first:]))
            mario, luigi = values
            assert mario < luigi <= mario * 1.15, f'Modest higher {action} in form{power}: {values}'
            if action != 'short':
                assert 1.075 <= luigi / mario <= 1.13, f'Full-jump increase stays modest: {values}'
            assert old[key][first]['gravity'] == new[key][first]['gravity'], 'Native initial rising gravity is retained'
            native_forces = {r['gravity'] for r in old[key]}
            assert {r['gravity'] for r in new[key]} <= native_forces, 'The same native rise/fall force values remain in use'
            for a, b in zip(old[key], new[key]):
                assert a['fallGravity'] == b['fallGravity'], 'Native falling and A-release force is retained'
            heights[action] = dict(mario=mario, luigi=luigi, increase_percent=round((luigi / mario - 1) * 100, 2))

        for action in ('jump', 'short'):
            key = (action, power)
            a, b = old[key][0], new[key][0]
            velocity = lambda r: (int(r['vy']) if int(r['vy']) < 128 else int(r['vy']) - 256) + int(r['yForce']) / 256
            assert velocity(b) - velocity(a) == -51 / 256, 'Only the requested dry initial jump fraction differs'

        braking = {}
        for action in ('coast', 'reverse'):
            a, b = old[(action, power)][0], new[(action, power)][0]
            native = int(a['brakeLow']) + 256 * int(a['brakeHigh'])
            changed = int(b['brakeLow']) + 256 * int(b['brakeHigh'])
            assert changed == native - native // 8, 'Ground braking is exactly native minus one eighth'
            braking[action] = dict(mario_force=native, luigi_force=changed,
                                   reduction_percent=round((1 - changed / native) * 100, 2))
        metrics.append(dict(power=power, jump_heights=heights, ground_braking=braking))
    return dict(character=8, result='passed', control_checkpoint=meta['checkpoint'],
                identical_environment_trials=18, identical_acceleration_prefixes=6,
                metrics=metrics)
