"""Root complete frozen friction matrices, two mapper workers, no native."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/agent49o2-sophia-friction-checker-e'
OUT=ROOT/'build/verification/root49o2-sophia-friction-c2b-cpu-full-f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BINDINGS={'mmc3':'4184ac25201b0b3d3e42299a09d1d43c28ce9a20ba0168473ccd00578c7d6a32',
          'mmc5':'4adcc4dd4fea86b06e7f8e0115c5c2b541f21fbe94177531d514b23b800427af'}

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'frozen.json')=='6d1881cbb2b22175be6899035a11692e1db94b24aa62f41bbbd3bfdffad3ebdb'
    frozen=json.loads((PACKET/'frozen.json').read_text())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    for mapper,h in BINDINGS.items():
        assert sha(PACKET/f'binding-{mapper}.json')==h
        smoke=json.loads((ROOT/f'build/verification/root49o2-sophia-friction-c2b-cpu-smoke-{mapper}-a.json').read_text())
        assert smoke['status'].startswith('PASS_')and smoke['cases']==512
    current=json.loads((ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in current.items())
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+20_000_000+225_000_000<50_000_000_000
    OUT.mkdir();suites=('hot','wide-middle','wide-outer','flags','callers','caller-flags')
    report={'status':'running-frozen-friction-matrices','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'frozen_checker_sha256':sha(PACKET/'frozen.json'),
            'workspace_before':used,'own_reserve':20_000_000,'other_future_reserve':225_000_000,'cases':[]}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run_mapper(mapper):
        rows=[]
        for suite in suites:
            out=OUT/f'{mapper}-{suite}.json';log=out.with_suffix('.log')
            command=[sys.executable,str(PACKET/'verify_cpu.py'),'--binding',str(PACKET/f'binding-{mapper}.json'),
                     '--binding-sha256',BINDINGS[mapper],'--suite',suite,'--seconds','1800','--out',str(out)]
            with log.open('wb')as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
            result=json.loads(out.read_text())if out.exists()else None
            row={'mapper':mapper,'suite':suite,'command':command,'exit':r.returncode,
                 'report_sha256':sha(out)if out.exists()else None,'log_sha256':sha(log),'result':result}
            rows.append(row)
            (OUT/f'{mapper}-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
            if r.returncode!=0:break
        return rows
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        for f in concurrent.futures.as_completed([pool.submit(run_mapper,m)for m in BINDINGS]):report['cases']+=f.result();save()
    assert all(sha(ROOT/n)==h for n,h in current.items())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    passed=len(report['cases'])==12 and all(r['exit']==0 and r['result']['status'].startswith('PASS_')for r in report['cases'])
    report.update(status='PASS_ALL12_FROZEN_FRICTION_CPU_MATRICES'if passed else'NEGATIVE_FROZEN_FRICTION_CPU_MATRIX',
                  workspace_after=workspace_bytes(ROOT),
                  qualification='Actual compiled pure helpers/callers only, exact physical RAM/status/stack/write lineage/cycles. Native interrupts, APU/PPU, performance and ordinary gameplay acceptance remain separate.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json')}));assert passed

if __name__=='__main__':main()
