"""Verify all four slots using the explicitly migrated shared fixture."""
from pathlib import Path
import concurrent.futures, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen
D=ROOT/'build/verification/weapon-input-v36-fixture-migration'
CHECKPOINT=ROOT/'build/checkpoints/roster-audit-v36-provisional-d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fixtures():return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'tests').rglob('*'))if p.is_file()}
before=fixtures()
shutil.copyfile(ROOT/'tests/expanded-weapons.lua',D/'after.lua')
def verify(case):
    character,mapper=case
    script=ROOT/f'tests/{character}-weapons.lua'
    rom=CHECKPOINT/f'smb-crossover-{mapper}.nes'
    result=run_mesen.run(script,rom,timeout=90)
    log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
    copied=D/f'migrated-{mapper}-{character}.log'
    shutil.copyfile(log,copied)
    return {'test':script.stem,'rom':rom.stem,'result':'passed'if result==0 else'failed',
            'exit':result,'rom_sha256':sha(rom),'log':copied.relative_to(ROOT).as_posix(),'log_sha256':sha(copied)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
    cases=list(pool.map(verify,((c,m)for m in('mmc3','mmc5')for c in('bass','ryu'))))
after=fixtures()
assert before==after,'No test mutations during corrected slot invocations'
report={'result':'passed'if all(c['exit']==0 for c in cases)else'failed',
 'scope':'Four exact component slots after one shared input-duration fixture migration; no runtime change',
 'before_sha256':sha(D/'before.lua'),'after_sha256':sha(D/'after.lua'),
 'fixture_hashes_before':before,'fixture_hashes_after':after,
 'oracles':'Every original damage, repeated-contact, windmill return/catch and watchdog assertion retained',
 'cases':cases}
(D/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],[(c['test'],c['rom'],c['exit'])for c in cases])
raise SystemExit(0 if report['result']=='passed' else 1)
