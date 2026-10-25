"""Retain the rejected wrapper calls, then replay the actual successful routes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    # This wait owns no emulator. The original native worker finishes first.
    while True:
        q=json.loads((a.batch/'progress.json').read_text())
        if q['complete']:break
        time.sleep(2)
    rows=[]
    for r in q['routes']:
        if r['discovery_exit']!=0:continue
        folder=Path(r['folder']);m=json.loads((folder/'manifest.json').read_text())
        assert m['ROM_sha256']==sha(a.rom) and m['result']['cleared'] and m['result']['deaths']==0
        # Preserve the actual CLI rejection: this was a wrapper-argument
        # error, before any emulator/replay ran, never a game failure.
        log=a.batch/('replay-'+r['identity']+'-'+r['mode']+'.log')
        assert r['replay_exit']==2 and 'unrecognized arguments: --batch' in log.read_text()
        rows.append(dict(identity=r['identity'],mode=r['mode'],passed=True,folder=str(folder),manifest_sha256=sha(folder/'manifest.json')))
    index=a.output/'discoveries.json'
    index.write_text(json.dumps(dict(ROM_sha256=sha(a.rom),phase='discover',runs=rows,
        parent_progress_sha256=sha(a.batch/'progress.json'),scope='Explicit successful current-hash discoveries only; original rejected CLI invocations retained.'),indent=2)+'\n')
    assert rows
    cmd=[sys.executable,str(ROOT/'tools/audit/replay_roster_pf.py'),'--rom',str(a.rom),
        '--discoveries',str(index),'--output',str(a.output/'direct')]
    with (a.output/'replay.log').open('w') as f:z=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    print('replay exit',z.returncode,flush=True);return z.returncode
if __name__=='__main__':raise SystemExit(main())
