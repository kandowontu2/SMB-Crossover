"""Bound the score repair, preserve literal baselines, run relevant native cases."""
from pathlib import Path
import json,hashlib,subprocess,sys,concurrent.futures
R=Path(__file__).resolve().parents[2];O=R/'build/verification/score-anchor-aq';assert not O.exists();O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def labels(p):
 out={}
 for line in p.read_text().splitlines():
  if line.startswith('al '):
   _,value,name=line.split();out[name]=int(value,16)
 return out
layout=[]
for mapper in ('mmc3','mmc5'):
 a=R/'build'/f'smb-crossover-{mapper}.nes';b=R/'build/checkpoints/terrain-publication-af/build'/a.name
 aa,bb=a.read_bytes(),b.read_bytes();al,bl=labels(a.with_suffix('.lbl')),labels(b.with_suffix('.lbl'))
 assert all(al.get(k)==v for k,v in bl.items()),{k:(v,al.get(k))for k,v in bl.items()if al.get(k)!=v}
 start=16+62*8192+bl['.SetupFloateyNumber']-0x8000;tail=16+36*8192+0x1fc0
 allowed=set(range(start,start+19))|set(range(tail,tail+64))
 changed=[i for i,(x,y)in enumerate(zip(aa,bb))if x!=y];assert all(i in allowed for i in changed)
 assert bb[tail:tail+64]==bytes([255])*64
 assert aa[:16]==bb[:16]and aa[16+512*1024:]==bb[16+512*1024:]
 assert (R/'build'/f'smb-crossover-{mapper}-baseline.nes').read_bytes()==(R/'build/checkpoints/score-anchor-before-al/build'/f'smb-crossover-{mapper}-baseline.nes').read_bytes()
 layout.append(dict(mapper=mapper,ROM_sha256=sha(a),parent_AF_sha256=sha(b),changed_bytes=len(changed),changed_banks=sorted({(i-16)//8192 for i in changed}),all_old_label_addresses_unchanged=True,only_resident_stub_and_old_FF_tail_change=True,no_new_RAM=True,literal_baseline=True,new_A_tail_target=al['.ScorePopupSetup']))
(O/'layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
names=['score-popup-location','terrain-coin-publication','bill-stomp','mario-powerup-fire-arena','samus-pickup-sfx','world-springs','bill-flagpole-full','remaining-source-sfx','link-source-enemy-effects','simon-source-enemy-effects','ryu-source-enemy-effects']
def test(name,mapper):
 p=O/f'{name}-{mapper}.log'
 with p.open('wb')as f:q=subprocess.run([sys.executable,str(R/'tools/run_mesen.py'),str(R/'tests'/(name+'.lua')),str(R/'build'/f'smb-crossover-{mapper}.nes'),'--timeout','90'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 text=p.read_text(encoding='utf-8',errors='replace');return dict(test=name,mapper=mapper,exit=q.returncode,passed=q.returncode==0 and 'PASS 'in text,log_sha256=sha(p))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
 for z in pool.map(lambda pair:test(*pair),[(n,m)for m in ('mmc3','mmc5')for n in names]):
  results.append(z);(O/'partial.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print('SCORE_REGRESSION',z['test'],z['mapper'],z['passed'],flush=True)
(O/'summary.json').write_text(json.dumps(dict(layout=layout,results=results,passed=all(z['passed']for z in results),goal_complete=False),indent=2)+'\n',encoding='utf-8')
