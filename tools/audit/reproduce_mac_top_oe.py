"""Repeat the already recorded failing Mac inputs with passive query logging."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--replay',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expect-fixed',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);source=a.replay.resolve();out=a.output.resolve()
    run=(source/'run.lua').read_text();old='out='+json.dumps(source.as_posix()+'/');new='out='+json.dumps(out.as_posix()+'/')
    assert run.count(old)==1;run=run.replace(old,new).replace('capture=1,','capture=0,')
    anchor='dofile(';at=run.index(anchor)
    debug=a.rom.with_suffix('.dbg');text=debug.read_text()if debug.exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    symbols={}
    for line in text.splitlines():
        if not line.startswith('sym\t'):continue
        q=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
        if 'val'in q:symbols[q['name'].strip('"')]=int(q['val'],0)
    aliases=''.join('L.'+n+'='+str(symbols[n])+'\n'for n in ['LmOldX','LmOldPage','LmOldY','BlockBuffer_Y_Adder'])
    observer=aliases+'MAC_EXPECT_FIXED='+('true'if a.expect_fixed else'false')+'\nMAC_OBSERVE_OUT='+json.dumps(out.as_posix()+'/')+'\ndofile('+json.dumps((ROOT/'tools/audit/observe_mac_top_oe.lua').as_posix())+')\n'
    script=out/'run.lua';script.write_text(run[:at]+observer+run[at:])
    z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),
        '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,capture_output=True,text=True)
    (out/'host.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2000:]
    if a.expect_fixed:
        observed=json.loads((out/'fixed-observer.json').read_text());assert observed['passed']and observed['invalid_native_queries']==0
        q=dict(passed=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),accepted=False,observed=observed,
               recorded_controller_source=str(source/'inputs.csv'),
               scope='Configured retained hard controller prefix on the fixed candidate through3200native frames. Passive observer confirms actual out-of-domain samples are rejected and no such sample reaches the native getter, with no death. This bounded scene-domain observation is separate from complete fresh route proof.')
        (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return
    assert (out/'trace.csv').read_bytes()==(source/'trace.csv').read_bytes()
    rows=list(csv.DictReader((out/'invalid-queries.csv').open()));solid=[r for r in rows if int(r['tile'])]
    assert rows and solid
    q=dict(reproduced=True,known_bug_present=True,accepted=False,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
           exact_recorded_trace=True,invalid_queries=len(rows),nonempty_invalid_queries=len(solid),examples=solid[:12],
           scope='Passive logging of original recorded hard route. Native side queries address cells outside the32..239 terrain domain and return nonzero tiles. This proves the retained failure, not a repaired candidate.')
    (out/'reproduction.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
