"""Real compiled constructor/phase/control/world/export fixtures, no emulator."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_host_lifecycle_model_1102_v12 as C
W,O=C.W,C.O


def main():
 b=W.scoped_load(C.BASE);results=[]
 for height,recipe,start,pipe,finish in [(0,'right',48,192,320),(16,'stop-up',48,192,320),(32,'stop-up',48,192,320),(48,'stop-up',48,192,320),(64,'stop-up',48,192,320),(32,'run-A',48,192,320),(64,'stop-up',304,448,576)]:
  h=C.World(b,x=start);h.terrain(lambda x,y:0x54 if y>=208 or(height and pipe<=x<pipe+32 and y>=208-height)else 0)
  before=bytes(h.s);assert h.s[0x60e:0x61c].hex()==('80'+(start+8).to_bytes(2,'little').hex()+'8000db96ff000000000000')
  assert h.s[0x6cf]==5 and h.s[0x6ee]==0
  rows=[];stage='approach';age=0;row=dict(foot=208)
  for f in range(900):
   x=h.x();pad=1
   if height:
    if stage=='approach'and x>=pipe-40:stage='launch'if recipe=='run-A'else'wait';age=0
    if stage=='wait':
     pad=0
     if h.s[0x617]==15 and h.s[0x618]==0:stage='launch';age=0
    if stage=='launch':
     pad=(8 if recipe=='stop-up'else 0x81)if age<64 else 0xc9
     if h.s[0x618]in [2,6]:pad=8
     age+=1
   if x>pipe+40:pad=1
   if x>finish and row['foot']in range(208,212):break
   row=h.step(pad)
   assert row['nativeX']==(row['X']-8)&65535
   assert(row['nativeY']+((row['nativeYHigh']-1)<<8))==row['foot']-32
   assert row['cameraSample']==row['nativeX']&255
   if f%30==0:rows.append(dict(Main=f,**row))
   if row['foot']>=240 or h.s[0x60e]==255:break
  results.append(dict(pipe_height=height,controller=recipe,start_native_X=start,pipe_world_X=pipe,cleared_and_landed=x>finish and 208<=row['foot']<=211,last=row,minFoot=min(r['foot']for r in rows),source_updates=h.steps,CPU=[min(h.cost),max(h.cost)],remaining_fixture_callbacks=dict(h.calls),trace=rows))
 q=dict(passed=all(r['cleared_and_landed']for i,r in enumerate(results)if i!=5)and not results[5]['cleared_and_landed'],private_CPU_only=True,native_emulator=False,ROM_SHA256=C.PIN,host_ROM_created=False,source_phase_and_constructor_and_native_exports_compiled=True,results=results,scope='Actual native1966 fields/buffers/material authority and compiled source constructor/phase0projection/phase1empty/phase3controls/phase4fallcontact/export. Original audio callbacks remain genuine donor instruction fixture services; owner/cold/auth/scene/death/combat/menu remain unbound, no native playability/helper/1-1 qualification.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'host-life-v12.bin',O/'host-render-v11.bin',O/'world-coordinates-v7.bin',C.BASE]})
 (O/'host-life-CPU-v12.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items()if k!='trace'}for r in results]));assert q['passed']


if __name__=='__main__':main()
