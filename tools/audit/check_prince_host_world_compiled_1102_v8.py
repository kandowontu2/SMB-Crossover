"""Compiled native world fixtures; compact receipts, no emulator or ROM."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_host_world_compiled_1102_v8 as C
import prince_host_world_1102_v6 as W
O=C.O


def main():
 results=[];b=W.scoped_load(W.BASE)
 for height,recipe in [(0,'right'),(16,'stop-up'),(32,'stop-up'),(48,'stop-up'),(64,'stop-up'),(32,'run-A')]:
  h=C.World(b);h.terrain(lambda x,y:0x54 if y>=208 or(height and 192<=x<224 and y>=208-height)else 0)
  h.inspect_tiles=True
  rows=[];stage='approach';age=0;row=dict(foot=208)
  for f in range(700):
   x=h.x();pad=1
   if height:
    if stage=='approach'and x>=152:stage='launch'if recipe=='run-A'else'wait';age=0
    if stage=='wait':
     pad=0
     if h.s[0x617]==15 and h.s[0x618]==0:stage='launch';age=0
    if stage=='launch':
     pad=(8 if recipe=='stop-up'else 0x81)if age<64 else 0xc9
     if h.s[0x618]in [2,6]:pad=8
     age+=1
   if x>232:pad=1
   if x>320 and row['foot']in range(208,212):break
   try:row=h.step(pad)
   except Exception as error:raise AssertionError((height,recipe,f,stage,pad,rows[-4:],str(error)))from error
   if f%30==0:rows.append(dict(NMI=f,**row))
   if row['foot']>=240 or h.s[0x60e]==255:break
  results.append(dict(pipe_height=height,controller=recipe,cleared_and_landed=x>320 and 208<=row['foot']<=211,last=row,maxX=max(r['X']for r in rows),minFoot=min(r['foot']for r in rows),trace=rows,remaining_Python_callbacks=dict(h.calls)))
 q=dict(passed=all(r['cleared_and_landed']for r in results[:5])and not results[5]['cleared_and_landed'],compiled_world_model_only=True,host_ROM_created=False,ROM_SHA256=W.PIN,results=results,scope='Original animation/movement/control/postcontact plus compiled original coordinates and compiled native terrain/material/alignment leaves. Python provides phase scheduling and geometry metadata export; no native owner/menu/update/camera/health/combat or1-1 claim.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),R/'tools/reference/prince_host_world_1102_v8.s',O/'host-world-v8.bin',O/'world-coordinates-v7.bin',O/'contact-core.bin']})
 (O/'host-world-compiled-v8.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items()if k!='trace'}for r in results]));assert q['passed'],'Compiled source/native traversal fixture failed'


if __name__=='__main__':main()
