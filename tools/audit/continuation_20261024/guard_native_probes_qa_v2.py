from pathlib import Path
import subprocess,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'guards-v1';O.mkdir(exist_ok=False)
source=json.loads((P/'routes-v1/replay-index.json').read_text());report=dict(complete=False,passed=False,ROM_sha256=source['ROM_sha256'],goal_complete=False,runs=[])
for row in source['runs']:
 assert row['passed'];name=row['identity']+'-'+row['mode'];out=O/name
 with(O/(name+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(R/'tools/audit/reproduce_sophia_lock_og.py'),'--rom',str(P/'candidate.nes'),'--route',row['folder'],'--output',str(out),'--expect','repaired','--until-clear','--movement'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 q=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else{}
 result=dict(identity=row['identity'],mode=row['mode'],exit=p.returncode,passed=p.returncode==0 and q.get('passed')is True,proof=str(out/'proof.json'))
 report['runs'].append(result);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(result),flush=True)
report['complete']=True;report['passed']=all(r['passed']for r in report['runs']);(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
