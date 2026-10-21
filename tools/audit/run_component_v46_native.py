"""Run frozen v2 native case suites in order, preserving any first failure."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
packet=ROOT/'build/verification/samus-idle45-native-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(packet/'freeze.json')=='454d355b21438b51c118bed8ec430965d3f67a39264c4d63689a7076a0e44aea'
out=ROOT/'build/verification/component46-native-v2-root-a'
out.mkdir(exist_ok=False)
report=dict(result='running',seeded_units_not_routes=True,freeze_sha256=sha(packet/'freeze.json'),runs=[])
rp=out/'report.json'

def call(tag,cmd):
    log=out/(tag+'.log')
    print('START',tag,flush=True)
    with log.open('w')as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    report['runs'].append(dict(tag=tag,command=cmd,exit=r.returncode,log_sha256=sha(log)))
    if r.returncode:report['result']='failed-preserved'
    rp.write_text(json.dumps(report,indent=2)+'\n')
    print('END',tag,r.returncode,flush=True)
    if r.returncode:raise SystemExit(r.returncode)

for mapper in('mmc5','mmc3'):
    tags=[]
    for side,cp in(('control45','roster-audit-v45'),('candidate46','roster-audit-v46-provisional-a')):
        rom=ROOT/'build/checkpoints'/cp/f'smb-crossover-{mapper}.nes'
        tag=f'{side}-{mapper}-root-a';tags.append(tag)
        call(tag,[sys.executable,str(packet/'native_run.py'),'--rom',str(rom),'--sha256',sha(rom),'--tag',tag])
    comparison=out/f'comparison-{mapper}.json'
    call('compare-'+mapper,[sys.executable,str(packet/'check_suite.py'),'--before',str(packet/f'suite-{tags[0]}.json'),
        '--after',str(packet/f'suite-{tags[1]}.json'),'--out',str(comparison)])
report['result']='all-native-suites-and-comparisons-passed'
rp.write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],flush=True)
