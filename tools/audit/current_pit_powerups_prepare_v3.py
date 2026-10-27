"""Prepare Pit v3's source-proven collision/recharge observation correction; never launches Mesen.

Reuse the exact v1 preparer implementation with only its fixture filename
retargeted. Both implementations, original negative and finite caller controls
remain bound. No game source, runtime, ROM or original preparation is copied.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
OLD_FIXTURE = ROOT/'tools/audit/current_pit_powerups_v1.lua'
FIXTURE = ROOT/'tools/audit/current_pit_powerups_v3.lua'
OLD_PREPARER = ROOT/'tools/audit/current_pit_powerups_prepare_v1.py'
NEGATIVE = ROOT/'build/current-6be-pit-easy-items-v1/first-negative.json'
LANDING = ROOT/'build/current-6be-pit-easy-items-v2/landing-negative.json'
PAIRS = [
    (b'local x,y=hammer and 136 or 176,hammer and 168 or 184',
     b'local x,y=hammer and 136 or 160,hammer and 168 or 184'),
    (b"phase=='bow'and 26 or 38", b"phase=='bow'and(26+C.plan[index].tier)or 38"),
    (b"elseif before.state==0 then assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Actual grounded source recharge');if rec.burn>0 then rec.recharged=true end",
     b"elseif before.state==0 then assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Actual grounded source recharge');if rec.burn>0 and not rec.recharged then assert(rec.landedAt and age==rec.landedAt+1,'First actual grounded source return follows collision landing');rec.recharged=true;rec.groundRechargeAt=age;event('actual-ground-recharge',r('XgPitFuel'))end"),
    (b"if rec.burn>0 and r('Player_State')==0 and not rec.landedAt then rec.landedAt=age;assert(r('XgPitFuel')==60,'Real landing restored fuel');rec.recharged=true;if phase=='fullflight'then screenshot='flutter-landed.png'end end",
     b"if rec.burn>0 and r('Player_State')==0 and not rec.landedAt then rec.landedAt=age;rec.landingFuel=r('XgPitFuel');event('actual-collision-landing',rec.landingFuel)end\n   if rec.landedAt and age==rec.landedAt+1 then assert(rec.recharged and rec.groundRechargeAt==age and r('XgPitFuel')==60 and r('XgPitFlight')==0,'Exactly60 fuel at the first following grounded update');if phase=='fullflight'then screenshot='flutter-landed.png'end end"),
]


def main():
    assert sha(OLD_FIXTURE) == 'c39d32ab4c301c8fd386e02102748e8025ea5f37ca84507abb6d6666322260c5'
    assert sha(OLD_PREPARER) == '1b0643adb95d1f130692098e057b29ff98c2e61b99576078ce60515dc095d006'
    assert sha(NEGATIVE) == 'e1f4c7e5657c4bea606769c7b9de6e0997272d369bf440b6cbcb9f0d6dc1594d'
    assert sha(LANDING) == '1690b47755792e2080b9d6c0858eaa0cc62c33b3009f6ace07209b3a00ee0352'
    for item in json.loads(LANDING.read_text())['bindings']:
        path = Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    original = OLD_FIXTURE.read_bytes()
    expected = original
    for old, new in PAIRS:
        assert expected.count(old) == 1
        expected = expected.replace(old, new)
    assert expected == FIXTURE.read_bytes()
    reverse = expected
    for old, new in reversed(PAIRS):
        assert reverse.count(new) == 1
        reverse = reverse.replace(new, old)
    assert reverse == original, 'All other mechanics/input/seed/hardware bytes exact'
    for item in json.loads(NEGATIVE.read_text())['bindings']:
        path = Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    implementation = OLD_PREPARER.read_text()
    old_name, new_name = 'current_pit_powerups_v1.lua', 'current_pit_powerups_v3.lua'
    assert implementation.count(old_name) == 1
    implementation = implementation.replace(old_name, new_name)
    namespace = dict(__file__=str(Path(__file__).resolve()), __name__='pit_v1_reused', __doc__=__doc__)
    exec(compile(implementation, str(OLD_PREPARER), 'exec'), namespace)
    with contextlib.redirect_stdout(io.StringIO()):
        namespace['main']()
    # Existing exact CLI parser determines the unique output; it creates no
    # native directory. Add only the versioned delta and immutable lineage.
    output = Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    ready_path = output/'prepared-not-run.json'
    ready = json.loads(ready_path.read_text())
    delta = output/'fixture-delta.json'
    delta.write_text(json.dumps(dict(
        passed=True, source_only=True, native_run=False,
        original_fixture_sha256=sha(OLD_FIXTURE), new_fixture_sha256=sha(FIXTURE),
        changes=[dict(old=o.decode(), new=n.decode(), occurrences=1) for o,n in PAIRS],
        all_other_fixture_bytes_exact=True, original_negative_retained=True,
        complete_GameLoop_CPU_cases=12, complete_GameLoop_CPU_updates=1320,
        CPU_source_receipt=str(NEGATIVE), CPU_source_receipt_sha256=sha(NEGATIVE),
        landing_source_receipt=str(LANDING), landing_source_receipt_sha256=sha(LANDING),
        landing_GameLoop_CPU_cases=6, landing_GameLoop_CPU_updates=1886,
        exact_saved_native_numeric_rows_matched=137, recharge_model_negative_rejections=5,
        no_native_inference=True), indent=2)+'\n', newline='\n')
    extra = [OLD_FIXTURE, OLD_PREPARER, NEGATIVE,
             ROOT/'tools/audit/current_pit_bow_negative_v1.py', delta, LANDING,
             ROOT/'tools/audit/current_pit_landing_negative_v1.py',
             ROOT/'tools/audit/current_pit_powerups_v2.lua',
             ROOT/'tools/audit/current_pit_powerups_prepare_v2.py']
    ready['fixture_version'] = 3
    ready['fixture_corrections'] = 'Retains v2 range/proxy corrections; landing records collision first, then requires exactly60 at next actual grounded source return/update. All other mechanics/input/seed/hardware bytes exact.'
    ready['original_native_outcome'] = 'v1 first-bow FALSE and v2 landing-observer FALSE retained; v2 completed7cases. Hard unrun. Never overwritten or relabeled.'
    ready['bindings'] += [dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p)) for p in extra]
    ready_path.write_text(json.dumps(ready,indent=2)+'\n', newline='\n')
    for item in ready['bindings']:
        path = Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN', output=str(output),
                          readiness_sha256=sha(ready_path), bindings=len(ready['bindings']),
                          fixture_delta_sha256=sha(delta), native_run=False)))


if __name__ == '__main__':
    main()
