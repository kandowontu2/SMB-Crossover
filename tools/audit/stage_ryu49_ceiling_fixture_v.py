"""Stage a source-backed portable ceiling assertion plus old-build negatives.

This does not replace main or the frozen candidate's original test files.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import importlib.util
import argparse
import time

R = Path(__file__).resolve().parents[2]
H = R / 'build/verification/root49-ryu-ceiling-fixture-v'
U = R / 'build/verification/root49-ryu-ceiling-timing-u'
P = R / 'build/verification/agent-lsr-s2-head-n2-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare():
    assert not H.exists()
    prep = json.loads((U / 'preparation.json').read_text())
    for b in prep['bindings']:
        result = Path(b['folder']) / 'result.json'
        assert json.loads(result.read_text())['status'] == 'PASS'
    original = R / 'tests/ryu-ground-wall-launch.lua'
    assert sha(original) == prep['original_fixture_sha256']
    text = original.read_text()
    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    replace('local sourceLaunchVy,ceilingReceipts=nil,0', 'local sourceLaunchVy,ceilingReceipts=nil,0\nlocal ceilingLater')
    replace('active=q;firstJump=false;', 'active=q;ceilingLater=nil;firstJump=false;')
    needle = " row('completed-collision',launches[1])"
    replace(needle, needle + "\n if active.kind=='ceiling'and firstJump and r('Player_Y_Speed')<128 and velocity()>=0 then ceilingLater={age=age,vy=velocity()}end")
    replace('firstJump={y=', "firstJump={age=age,yFraction=r('MmYFraction')+256*r('MmYFraction',1),y=")
    old = "if q.kind=='ceiling'then check(j.yspeed<128 and ceilingReceipts>0,'actual overhead collision still reaches native stop and stops rising motion')"
    revised = """if q.kind=='ceiling'then
    -- SOURCE-CEILING-V: Ryu's largest unrotated HRect is27 NES pixels;
    -- foot=PY+32, roof bottom176. First launch -540/120 plus gravity
    -- 1400/7200 yields qVY=-282169 and top176.69444, strictly disjoint.
    -- A genuine head collision follows on a later update, not this first one.
    -- Original native-stop-at-first-update failures remain in the private run.
    local expectedVy=-294912+12743
    local actualYQ=j.y*65536+j.yFraction
    check(actualYQ==176*65536+expectedVy and math.abs(j.vy-expectedVy/65536)<1/131072,'source-disjoint first launch preserves exact integrated Y and VY')
    check(actualYQ+5*65536>176*65536 and j.yspeed>=128,'largest27px source envelope is disjoint and continues rising')
    check(ceilingReceipts>0 and ceilingLater and ceilingLater.age>j.age,'actual later overhead collision still reaches native stop and stops rising motion')"""
    replace(old, revised)
    H.mkdir()
    fixture = H / 'ryu-ground-wall-launch.lua'
    fixture.write_text(text)
    shutil.copyfile(original, H / 'original-ryu-ground-wall-launch.lua')
    bindings = []
    for variant in ['old-s2-negative', 'candidate-n2']:
        for mapper in ['mmc3', 'mmc5']:
            folder = H / (variant + '-' + mapper)
            (folder / 'tests').mkdir(parents=True)
            shutil.copyfile(fixture, folder / 'tests/ryu-ground-wall-launch.lua')
            shutil.copyfile(R / 'tests/menu-bootstrap.lua', folder / 'tests/menu-bootstrap.lua')
            rom = (R if variant == 'old-s2-negative' else P / 'source') / ('build/smb-crossover-' + mapper + '.nes')
            bindings.append(dict(name=variant+'-'+mapper, folder=str(folder), ROM=str(rom),
                ROM_sha256=sha(rom), fixture_sha256=sha(folder/'tests/ryu-ground-wall-launch.lua'),
                expected_pass=variant == 'candidate-n2'))
    refs = [original, R / 'tests/menu-bootstrap.lua', R / 'tools/run_mesen.py', U / 'preparation.json',
            *(Path(b['folder']) / 'result.json' for b in prep['bindings'])]
    (H / 'preparation.json').write_text(json.dumps(dict(status='STAGED_NOT_EXECUTED',
        script_sha256=sha(__file__), original_fixture_sha256=sha(original), revised_fixture_sha256=sha(fixture),
        references={str(p.relative_to(R)): sha(p) for p in refs}, bindings=bindings,
        scope='All20 arenas retained; source-correct first-update disjointness and genuine later stop are both required. Source/gameplay assertions outside the two ceiling arenas are unchanged.',
        runtime_changes=False, main_fixture_changed=False, original_negative_preserved=True), indent=2)+'\n')
    print('STAGED', sha(H / 'preparation.json'), flush=True)


def run(name):
    prep = json.loads((H / 'preparation.json').read_text())
    assert sha(__file__) == prep['script_sha256']
    assert all(sha(R/n) == h for n,h in prep['references'].items())
    b = next(b for b in prep['bindings'] if b['name'] == name)
    folder = Path(b['folder'])
    output = folder / 'result.json'
    assert not output.exists()
    script = folder / 'tests/ryu-ground-wall-launch.lua'
    assert sha(script) == b['fixture_sha256'] and sha(b['ROM']) == b['ROM_sha256']
    spec = importlib.util.spec_from_file_location('isolated_runner', R / 'tools/run_mesen.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = folder
    t = time.monotonic()
    code = module.run(script, Path(b['ROM']), timeout=120)
    verification = folder / 'build/verification'
    import csv
    rows = list(csv.DictReader(next(verification.glob('*-ryu-ground-wall-cases.csv')).open()))
    assert len(rows) == 20
    failed = [q for q in rows if q['result'] != 'PASS']
    matched = (code == 0 and not failed) if b['expected_pass'] else (code != 0 and len(failed) == 2 and all(q['kind']=='ceiling' for q in failed))
    result = dict(status='PASS_EXPECTED_CANDIDATE' if matched and b['expected_pass'] else 'PASS_DISTINGUISHING_OLD_NEGATIVE' if matched else 'UNEXPECTED_RETAINED',
        expected=b, native_exit=code, actual_cases=len(rows), failed_cases=failed,
        elapsed_seconds=time.monotonic()-t,
        artifacts={str(p.relative_to(folder)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in verification.glob('*') if p.is_file()},
        runtime_changes=False, main_fixture_changed=False, route_proof=False)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'], name, sha(output), flush=True)
    raise SystemExit(not matched)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--run')
    a = ap.parse_args()
    run(a.run) if a.run else prepare()
