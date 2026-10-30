"""Compile only an unlinked scheduler layout; install/execute no aliases."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
O=R/'build/ff-fx-epoch-workers-sizing-v1';S=R/'tools/reference/ff_fx_epoch_workers_proposal_v1.s'

def main():
    O.mkdir(exist_ok=False)
    cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','--create-full-dep',str(O/'workers.dep'),'-o',str(O/'workers.o'),str(S)]
    B.save(O/'validated-outputs.json',validate(cmd,O,cwd=R))
    p=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
    B.save(O/'compile.json',dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:
        print(json.dumps(dict(passed=False,unlinked=True,installed=False,error=p.stderr)),flush=True);return
    q=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(O/'workers.o')],cwd=R,text=True,capture_output=True)
    assert q.returncode==0
    B.write(O/'segments.txt',q.stdout)
    sizes=dict(re.findall(r'Name:\s*"([^"]+)"\s*Flags:[^\n]*\s*Size:\s*(\d+)',q.stdout))
    B.save(O/'sizing.json',dict(passed=True,unlinked=True,installed=False,aliases_executed=False,
        segments=sizes,raw_segment_report=q.stdout,bindings={str(f):B.sha(f)for f in[S,Path(__file__),O/'workers.o',O/'validated-outputs.json',O/'compile.json']}))
    print(q.stdout,flush=True)

if __name__=='__main__':main()
