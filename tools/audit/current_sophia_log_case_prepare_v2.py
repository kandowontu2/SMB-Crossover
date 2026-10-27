"""Prepare the logging-only Sophia successor; preserve the failed original."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', newline='\n')


def main():
    old = ROOT / 'build/current-bdf9-sophia-earned-hard-v1'
    new = ROOT / 'build/current-bdf9-sophia-earned-hard-v2'
    ready = old / 'prepared-not-run.json'
    assert sha(ready) == '8280a12e47df71a49ae75e59d621026066dac5992be6a257a14dc3da33da6a09'
    receipt = json.loads(ready.read_text())
    for item in receipt['bindings']:
        assert sha(item['path']) == item['sha256'], item['path']
    assert not new.exists()
    new.mkdir()
    before = 'stock(item<16 and item or C.plan[index].ammo_item)'
    after = 'stock(item<16 and item or C.plan[(rec and rec.case_index) or index].ammo_item)'
    fixture = (old / 'fixture.lua').read_text()
    assert fixture.count(before) == 1
    fixed = fixture.replace(before, after)
    assert fixed.replace(after, before) == fixture
    (new / 'fixture.lua').write_text(fixed, newline='\n')
    for name in ('config.json', 'source-controls.json', 'source-layout.json'):
        (new / name).write_bytes((old / name).read_bytes())
    run = (old / 'run.lua').read_text()
    assert run.count((old / 'fixture.lua').as_posix()) == 1
    (new / 'run.lua').write_text(run.replace((old / 'fixture.lua').as_posix(), (new / 'fixture.lua').as_posix()), newline='\n')
    cmd = json.loads((old / 'command.json').read_text())
    cmd['argv'] = [str(new / 'native') if x == str(old / 'native') else str(new / 'run.lua') if x == str(old / 'run.lua') else x for x in cmd['argv']]
    put(new / 'command.json', cmd)
    cfg = json.loads((old / 'config.json').read_text())
    controls = []
    for i, case in enumerate(cfg['plan']):
        logged_item = case['item']
        effective = logged_item if logged_item < 16 else case['ammo_item']
        assert isinstance(effective, int)
        controls.append(dict(case_index=i+1, item=logged_item, actual_stock_index=effective))
    # On a phase transition the retained rec still describes case9 (refill2),
    # while index already describes case10 (Hover) with no ammo_item field.
    assert cfg['plan'][8]['ammo_item'] == 2 and 'ammo_item' not in cfg['plan'][9]
    put(new / 'logging-controls.json', dict(passed=True, native_run=False, exact_one_expression_reverse=True,
        gameplay_controller_setup_plan_caps_guards_unchanged=True, cases=controls,
        original_negative='After native case9 genuine Homing refill4->6, phase logging used next-case metadata and raised nil arithmetic. Retain original CSV/log/launch.',
        correction='Read the ammunition index from the record being logged, including transitions; never mutate gameplay state.'))
    paths = {Path(x['path']) for x in receipt['bindings']}
    paths |= {ready, old / 'launch.json', old / 'native/earned-components.csv', Path(__file__)}
    paths |= set((old / 'native').glob('*.log'))
    paths |= set(new.iterdir())
    receipt.update(status='PREPARED_DO_NOT_RUN', native_run=False, passed=False, goal_complete=False,
        parent_ready_sha256=sha(ready), change='Logging-only record/case association; all gameplay/guards/caps unchanged.',
        bindings=[dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(paths)])
    put(new / 'prepared-not-run.json', receipt)
    print(json.dumps(dict(ready=str(new / 'prepared-not-run.json'), sha256=sha(new / 'prepared-not-run.json'), bindings=len(paths))))


if __name__ == '__main__':
    main()
