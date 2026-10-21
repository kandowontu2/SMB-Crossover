"""Check actual installed E artifacts and retain both mapper smoke exits."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-main-ice-e-smoke'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(c):
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for z in b['artifacts'].values():assert sha(R/z['path'])==sha(R/z['frozen_path'])==z['sha256']
def main():
    assert not O.exists();O.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
    assert sha(cp)=='65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b'
    c=json.loads(cp.read_text());exact(c);results=[]
    for mp in ['mmc3','mmc5']:
        p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),
          '--output',str(O),str(R/'tests/baseline.lua'),str(R/'build'/f'smb-crossover-{mp}.nes'),
          '--timeout','30'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=O/f'{mp}-host.log';log.write_bytes(p.stdout)
        results.append(dict(mapper=mp,exit=p.returncode,host_log_sha256=sha(log)))
        (O/'progress.json').write_text(json.dumps(dict(status='RUNNING',groups=results),indent=2)+'\n')
        assert p.returncode==0 and b'PASS boot, title, level load, player control, floor collision'in p.stdout,(mp,p.stdout)
        print('PASS',mp,flush=True)
    exact(c)
    files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in O.iterdir()if p.is_file()}
    report=dict(status='PASS_ACTUAL_INSTALLED_E_BOOT_TITLE_CONTROL_FLOOR_BOTH_MAPPERS',
      script_sha256=sha(__file__),checkpoint_sha256=sha(cp),sources_rehashed=457,generated_rehashed=11,
      primary_artifacts_rehashed=8,groups=results,files=files,goal_complete=False)
    (O/'review.json').write_text(json.dumps(report,indent=2)+'\n');print('DONE',sha(O/'review.json'),flush=True)
if __name__=='__main__':main()
