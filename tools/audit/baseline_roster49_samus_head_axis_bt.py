"""Compare retained private G assertions against unmodified F fixture behavior."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-head-axis-baseline-bt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not H.exists();H.mkdir();groups=[]
 for n in ['samus-zero-wall-contact','samus-head-bricks']:
  for mp in ['mmc3','mmc5']:
   fixture=R/f'tests/{n}.lua';out=H/f'{mp}-{n}';out.mkdir()
   rom=R/f'build/checkpoints/roster-audit-v49-freeze-render-fast-f/smb-crossover-{mp}.nes'
   q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(fixture),str(rom),'--timeout','180'],cwd=R,capture_output=True,text=True)
   log=H/f'{mp}-{n}-host.log';log.write_text(q.stdout+q.stderr)
   groups.append(dict(fixture=n,fixture_sha256=sha(fixture),mapper=mp,ROM_sha256=sha(rom),exit=q.returncode,log_sha256=sha(log),files={str(p.relative_to(H)):sha(p)for p in out.rglob('*')if p.is_file()}))
   (H/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(mp,n,q.returncode,flush=True)
 (H/'review.json').write_text(json.dumps(dict(script_sha256=sha(__file__),groups=groups,scope='Unmodified F baselines of the same two fixtures. Not a candidate acceptance or full suite.'),indent=2)+'\n')
 print('BASELINE_REVIEW',sha(H/'review.json'),flush=True)
if __name__=='__main__':main()
