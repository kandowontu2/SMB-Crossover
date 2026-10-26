"""Run unchanged finite control assertions on an explicitly hashed composition."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def binding(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--expected-candidate-sha256',required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--expected-parent-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 tools={n:ROOT/f'tools/audit/chip_hot_control_current6c_{n}_v1.py'for n in['caller','inputs','side','foreign','irq']};inputs=[a.candidate,a.candidate.with_suffix('.dbg'),a.candidate.with_suffix('.lbl'),a.parent,a.parent.with_suffix('.dbg'),a.parent.with_suffix('.lbl')]+list(tools.values());frozen=[binding(q)for q in inputs];assert sha(a.candidate)==a.expected_candidate_sha256 and sha(a.parent)==a.expected_parent_sha256
 receipts=[];commands=[]
 for name,tool in tools.items():
  assert all(sha(Path(q['path']))==q['sha256']for q in frozen),'Input drift'
  out=a.output/(name+'-cpu-v1');cmd=[sys.executable,str(tool),'--candidate',str(a.candidate),'--output',str(out)]
  if name!='irq':cmd+=['--parent',str(a.parent)]
  commands.append(cmd);proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(name+'.stdout.txt')).write_text(proc.stdout);(a.output/(name+'.stderr.txt')).write_text(proc.stderr);assert proc.returncode==0,(name,proc.stdout[-2000:],proc.stderr[-2000:]);proof=out/'proof.json';z=json.loads(proof.read_text());assert z['passed']and z['ROM_sha256']==a.expected_candidate_sha256
  if name!='irq':assert z['parent_ROM_sha256']==a.expected_parent_sha256
  receipts.append(binding(proof));print(name+' passed',flush=True)
 assert all(sha(Path(q['path']))==q['sha256']for q in frozen),'Final input drift'
 result=dict(passed=True,native_executed=False,production_mutated=False,candidate_ROM_sha256=a.expected_candidate_sha256,parent_ROM_sha256=a.expected_parent_sha256,unchanged_original_assertions_and_inputs=True,exact_commands=commands,CPU_checks=receipts,input_bindings=frozen,scope='New executions of the same frozen finite caller/input/side/foreign-continuation/IRQ controls on the actual explicit combined ROM. Historical captured-state CPU arenas remain controlled inputs, not fresh native states. No optimization/source/gameplay/native/adoption scope added.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),candidate_ROM_sha256=a.expected_candidate_sha256)))
if __name__=='__main__':main()
