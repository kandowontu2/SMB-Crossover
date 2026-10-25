"""Wait for the head worker, then qualify pause/restore with camera parity."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--script',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    q=dict(complete=False,passed=False,ROM_sha256=sha(a.rom),cases=[],goal_complete=False)
    def save():(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
    save()
    while True:
        if a.after.exists():
            h=json.loads(a.after.read_text())
            if h.get('complete'):assert h['passed'] and h['ROM_sha256']==q['ROM_sha256'];break
        time.sleep(2)
    for camera in [0,123,451]:
        out=a.output/str(camera)
        args=[sys.executable,str(ROOT/'tools/audit/guard_zelda_pause_pr.py'),'--rom',str(a.rom),'--script',str(a.script),'--output',str(out),'--camera',str(camera),'--exercise-status']
        z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(a.output/(str(camera)+'.log')).write_text(z.stdout+z.stderr)
        assert z.returncode==0,(camera,(z.stdout+z.stderr)[-1000:])
        result=json.loads((out/'interrupt-proof.json').read_text());binding=json.loads((out/'binding.json').read_text())
        assert result['passed'] and binding['ROM_sha256']==q['ROM_sha256']
        q['cases'].append(dict(camera=camera,folder=str(out),interrupts=result,binding_sha256=sha(out/'binding.json')));save();print(camera,'PASS',flush=True)
    q.update(complete=True,passed=True);save()
if __name__=='__main__':main()
