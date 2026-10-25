from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
rom=R/'build/checkpoints/native-items-px/candidate.nes';routes=D.parent/'2026-10-24-native-items-px/head-routes-v3';out=D/'cv3-current-qualification-v1';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(rom)=='18a05934bc95410bf058d239cc67e6c97851dfb575a144194ebf4643dc2a3438'
drivers={}
for key,name,count in [('capture','capture_direct_replay_ot.py',2),('guard','reproduce_sophia_lock_og.py',1)]:
 t=(R/'tools/audit'/name).read_text();anchor='ROOT=Path(__file__).resolve().parents[2]';assert t.count(anchor)==1
 t=t.replace(anchor,'ROOT=Path('+repr(R.as_posix())+')');assert t.count('capture=12,')==count;t=t.replace('capture=12,','capture=24,')
 p=out/(key+'-bound.py');p.write_text(t);drivers[key]=p
report=dict(passed=False,goal_complete=False,ROM_sha256=sha(rom),driver_sha256={k:sha(p)for k,p in drivers.items()},native_workers=1,runs=[],scope='Independent current-hash exact-input/trace replays, full direct physical PPU records, original immutable-code/SMC/stack/NMI/IRQ and scrolling bounds. Interval24discovery serialization is bound exactly; no outcome bounds relaxed. Human image review remains a separate sampled/local-window audit.')
for row in json.loads((routes/'results.json').read_text()):
 assert row['exit']==0 and row['result']['cleared']and row['result']['deaths']==0 and row['ROM_sha256']==report['ROM_sha256']
 name=row['identity']+'-'+row['mode'];route=Path(row['folder']);direct=out/('direct-'+name);guard=out/('guard-'+name);review=out/('review-'+name)
 def run(tag,cmd):
  with(out/(tag+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  return p.returncode
 c=run('capture-'+name,[sys.executable,str(drivers['capture']),'--rom',str(rom),'--route',str(route),'--output',str(direct),'--timeout','240'])
 g=run('guard-'+name,[sys.executable,str(drivers['guard']),'--rom',str(rom),'--route',str(route),'--output',str(guard),'--expect','repaired','--until-clear','--movement'])
 v=run('review-'+name,[sys.executable,str(R/'tools/audit/review_direct_route_pa.py'),'--rom',str(rom),'--capture',str(direct),'--discovery',str(route),'--guard',str(guard),'--output',str(review)])if c==g==0 else -1
 result=dict(identity=row['identity'],mode=row['mode'],capture_exit=c,guard_exit=g,review_exit=v,passed=c==g==v==0,capture=str(direct),guard=str(guard),review=str(review))
 report['runs'].append(result);(out/'progress.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(result),flush=True)
report['passed']=len(report['runs'])==6 and all(x['passed']for x in report['runs']);(out/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['passed']else 1)
