"""Exact palette-symbol cover for the three restored source poses."""
from pathlib import Path
import sys,json,time
import numpy as np
from scipy.optimize import Bounds,LinearConstraint,milp
from scipy.sparse import coo_matrix
from analyze_sprite_vertical_alignment import decode,encode,flip
R=Path(__file__).resolve().parents[2];O=R/'build/verification/new-roster-1-1-nd/bass-arm-optimized';O.mkdir(exist_ok=False)
plan=json.loads((O.parent/'bass-arm-plan/plan.json').read_text());reports=[]
for job in plan['jobs']:
 patterns=[decode(bytes.fromhex(v))for v in job['patterns']];im={}
 for t,a,x,y in reversed(job['parts']):
  for yy,row in enumerate(flip(patterns[t//2],a&64,a&128)):
   for xx,c in enumerate(row):
    if c:im.setdefault((x+xx,y+yy),(a&3,c))
 pixels=sorted(im);index={p:i for i,p in enumerate(pixels)};cand=[]
 for pal in sorted({p for p,c in im.values()}):
  own=[p for p in pixels if im[p][0]==pal]
  for y in range(min(y for x,y in own)-15,max(y for x,y in own)+1):
   for x in range(min(x for x,y in own)-7,max(x for x,y in own)+1):
    cover=[index[p]for p in own if x<=p[0]<x+8 and y<=p[1]<y+16]
    if not cover:continue
    pic=tuple(tuple(im.get((x+xx,y+yy),(None,0))[1]if im.get((x+xx,y+yy),(None,0))[0]==pal else 0 for xx in range(8))for yy in range(16))
    pat,flags=min((encode(flip(pic,h,v)),(64 if h else 0)|(128 if v else 0))for h,v in((0,0),(1,0),(0,1),(1,1)))
    cand.append(dict(x=x,y=y,pal=pal,flags=flags,cover=cover,pattern=pat))
 rows=list(range(-32,65));rr=[];cc=[];vv=[];n=len(cand);off=len(pixels);last=off+len(rows)
 for j,c in enumerate(cand):
  for i in c['cover']:rr.append(i);cc.append(j);vv.append(1)
  for i,y in enumerate(rows):
   if c['y']<=y<c['y']+16:rr.append(off+i);cc.append(j);vv.append(1)
  rr.append(last);cc.append(j);vv.append(1)
 matrix=coo_matrix((vv,(rr,cc)),shape=(last+1,n)).tocsc()
 low=np.r_[np.ones(len(pixels)),np.zeros(len(rows)+1)]
 started=time.monotonic();solution=None
 for budget in(6,7,8):
  upper=np.r_[np.full(len(pixels),np.inf),np.full(len(rows),budget),14]
  result=milp(c=np.ones(n),integrality=np.ones(n),bounds=Bounds(0,1),constraints=LinearConstraint(matrix,low,upper),options={'time_limit':20,'mip_rel_gap':0.0})
  if result.x is not None:solution=[c for c,v in zip(cand,result.x)if v>.5];break
 assert solution,job['pose']
 actual={};pool=[];parts=[]
 for c in solution:
  if c['pattern']not in pool:pool.append(c['pattern'])
  parts.append([pool.index(c['pattern'])*2,c['pal']|c['flags'],c['x'],c['y']])
  for i in c['cover']:actual[pixels[i]]=im[pixels[i]]
 assert actual==im
 peak=max(sum(c['y']<=s<c['y']+16 for c in solution)for s in rows);assert peak<=budget
 reports.append(dict(pose=job['pose'],pixels=len(pixels),parts=len(parts),peak_scanline=peak,seconds=time.monotonic()-started,candidates=n,exact_palette_symbols=True,solver=result.message))
 job.update(parts=parts,patterns=[p.hex()for p in pool])
 print(json.dumps(reports[-1]),flush=True)
(O/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'proof.json').write_text(json.dumps(reports,indent=2)+'\n')
