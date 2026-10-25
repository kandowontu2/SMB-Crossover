from pathlib import Path
import json,hashlib,subprocess,sys,concurrent.futures
R=Path(__file__).resolve().parents[2];O=R/'build/verification/terrain-repair-build-v';assert not O.exists();O.mkdir()
old=R/'build/checkpoints/footage-fixes-before-n'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def labels(p):
 out={}
 for line in p.read_text().splitlines():
  if line.startswith('al '):
   _,value,name=line.split();out[name]=int(value,16)
 return out
layout=[]
for mapper in ('mmc3','mmc5'):
 a=R/'build'/f'smb-crossover-{mapper}.nes';b=old/'build'/a.name
 aa,bb=a.read_bytes(),b.read_bytes();diff=[i for i,(x,y)in enumerate(zip(aa,bb))if x!=y]
 al,bl=labels(a.with_suffix('.lbl')),labels(b.with_suffix('.lbl'))
 moved={k:[v,al.get(k)]for k,v in bl.items()if al.get(k)!=v}
 assert not moved,moved
 assert len(diff)==14 and sorted({(i-16)//8192 for i in diff})==[62,63]
 assert aa[:16]==bb[:16]and aa[16+512*1024:]==bb[16+512*1024:]
 layout.append(dict(mapper=mapper,sha256=sha(a),old_sha256=sha(b),changed_bytes=len(diff),changed_banks=[62,63],every_old_label_address_unchanged=True,no_new_RAM=True))
(O/'layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
names=['character-select','player-outlines','mario-native-pipe-control','luigi-native-physics','bill-flagpole-full','samus-head-displacement','sophia-independent-weapons','world-springs','firebar-draw-admission','roster-stomp-audit','bill-inventory-202']
def test(name,mapper):
 log=O/f'{name}-{mapper}.log'
 with log.open('wb')as f:q=subprocess.run([sys.executable,str(R/'tools/run_mesen.py'),str(R/'tests'/(name+'.lua')),str(R/'build'/f'smb-crossover-{mapper}.nes'),'--timeout','90'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 t=log.read_text(encoding='utf-8',errors='replace');return dict(name=name,mapper=mapper,exit=q.returncode,passed=q.returncode==0 and 'PASS 'in t,log_sha256=sha(log))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
 for z in pool.map(lambda item:test(*item),[(n,m)for m in ('mmc3','mmc5')for n in names]):
  results.append(z);(O/'partial.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print('REGRESSION',z['name'],z['mapper'],z['passed'],flush=True)
(O/'summary.json').write_text(json.dumps(dict(layout=layout,results=results,passed=all(z['passed']for z in results),goal_complete=False),indent=2)+'\n',encoding='utf-8')
