"""Trace a retained controller prefix through Sophia's native freeze."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expect',choices=['freeze','repaired'],default='freeze')
    p.add_argument('--until-clear',action='store_true')
    p.add_argument('--movement',action='store_true');a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);route=a.route.resolve()
    run=(route/'run.lua').read_text();old='out='+json.dumps(route.as_posix()+'/')
    assert run.count(old)==1 and run.count('replay=nil')==1
    run=run.replace(old,'out='+json.dumps(out.as_posix()+'/'))
    run=run.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
    debug=a.rom.with_suffix('.dbg');text=debug.read_text()if debug.exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    symbols={};smc=None
    for line in text.splitlines():
        if line.startswith('seg\t'):
            seg=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
            if seg.get('name')=='"SMCCODE"':smc=seg
        if not line.startswith('sym\t'):continue
        q=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
        if 'val'in q:symbols[q['name'].strip('"')]=int(q['val'],0)
    for line in a.rom.with_suffix('.lbl').read_text().splitlines():
        q=line.split()
        if len(q)==3 and q[0]=='al':symbols[q[2].lstrip('.')]=int(q[1],16)
    aliases=''.join('L.'+n+'='+str(symbols[n])+'\n'for n in ['__SMCCODE_RUN__','__SMCCODE_SIZE__'])
    assert smc is not None
    start,size=int(smc['ooffs'],0),int(smc['size'],0)
    raw=a.rom.read_bytes()[start:start+size]
    aliases+='SOPHIA_SMC_ORIGINAL={'+','.join(str(b)for b in raw)+'}\n'
    observer=ROOT/'tools/audit/observe_sophia_lock_og.lua'
    frozen=out/'observer.lua';frozen.write_bytes(observer.read_bytes())
    pre=aliases+'SOPHIA_GUARD_UNTIL_CLEAR='+str(a.until_clear).lower()+'\nSOPHIA_EXPECT_REPAIRED='+str(a.expect=='repaired').lower()+'\nSOPHIA_LOCK_OUTPUT='+json.dumps(out.as_posix()+'/')+'\ndofile('+json.dumps(frozen.as_posix())+')\n'
    if a.movement:
        movement=out/'movement-observer.lua';movement.write_bytes((ROOT/'tools/audit/sophia_committed_observer_og.lua').read_bytes())
        pre+='dofile('+json.dumps(movement.as_posix())+')\n'
    at=run.index('dofile(');script=out/'run.lua';script.write_text(run[:at]+pre+run[at:])
    z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),
        '--timeout','120','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT)
    (out/'host.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-3000:]
    if a.until_clear:
        assert(out/'inputs.csv').read_bytes()==(route/'inputs.csv').read_bytes()
        assert(out/'trace.csv').read_bytes()==(route/'trace.csv').read_bytes()
    q=dict(passed=True,expectation=a.expect,accepted=False,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
           observed=json.loads((out/'observed.json').read_text()),controller_sha256=hashlib.sha256((route/'inputs.csv').read_bytes()).hexdigest(),
           observer_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),
           movement_observer_sha256=hashlib.sha256(movement.read_bytes()).hexdigest()if a.movement else None,
           driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           scope='Read-only recorded controller stream, execution outside ROM/declared SMC, immutable SMC write guard, PPU writes and native NMI/update progress. Until-clear mode requires exact independent input/trace bytes through the original real 1-2 endpoint. Movement observer, when present, records completed loop/body origins and the source-owned projectile borrow; PNG retention/review is separate.')
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
