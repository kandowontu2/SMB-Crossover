"""Freeze six legal cold-menu NMI controls: numeric modes0/1 and variants1/2/3."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expect-sha',required=True);p.add_argument('--routes',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--diagnostic',action='store_true');a=p.parse_args();assert sha(a.rom)==a.expect_sha;a.output.mkdir(parents=True,exist_ok=False);profiles=[]
 for mode in ['easy','hard']:
  for variant,name in enumerate(['octopus','twinbee','pentarou'],1):
   out=a.output/(name+'-'+mode);cmd=[sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_rebind.py'),'--parent',str(a.parent),'--parser-root',str(a.parser_root),'--output',str(out),'--rom',str(a.rom),'--expect-sha',a.expect_sha,'--route',str(a.routes/(name+'-easy')),'--behavior',mode,'--variant',str(variant),'--name',name]
   if not a.diagnostic:cmd+=['--strict']
   if mode=='hard':cmd+=['--adaptive']
   r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;z=json.loads((out/'preparation.json').read_text(encoding='utf-8'));profiles.append(dict(name=name,mode=int(mode=='hard'),variant=variant,packet=str(out),script=z['script'],preparation_sha256=sha(out/'preparation.json'),script_sha256=z['script_sha256'],input_mode=z['input_mode'],command=cmd))
 q=dict(prepared=True,goal_complete=False,native_passed=False,ROM_sha256=a.expect_sha,script_sha256=sha(Path(__file__)),profiles=profiles,scope='Six cold-menu640 native fixtures. Easy exact historical8ff controls rebound to explicit ROM; Hard legal adaptive menu/route controls with full new input recording and numericRAMreadback. No emulated state/OAM/resource writes, no ready-state injection. Not a full route clear.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(profiles=len(profiles),preparation_sha256=sha(a.output/'preparation.json'))))
if __name__=='__main__':main()
