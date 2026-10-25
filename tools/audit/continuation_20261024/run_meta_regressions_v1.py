from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
out=D/'meta-regressions-v1';out.mkdir(exist_ok=False);results=[]
for mode in ['easy','hard']:
 for physical in [True,False]:
  name=mode+('-physical'if physical else'-moves');folder=out/name
  cmd=[sys.executable,str(R/'tools/audit/check_meta_moves_nu.py'),'--rom',str(rom),'--output',str(folder)]
  if mode=='hard':cmd+=['--hard']
  if physical:cmd+=['--physical']
  with(out/(name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  result=json.loads((folder/'result.json').read_text())if(folder/'result.json').exists()else None
  results.append(dict(name=name,exit=p.returncode,result=result));(out/'results.json').write_text(json.dumps(dict(passed=all(x['exit']==0 for x in results),ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),runs=results),indent=2)+'\n');print(name,p.returncode,flush=True)
