"""Natural original first-writer ownership of actor motion/contact state."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
from recover_prince_core_1101_v1 import O


def main():
 c=P.boot();total=0
 for i in range(900):P.frame(c,16 if 120<=i<123 or 300<=i<303 or 600<=i<603 else 0)
 names={0x60f:'Xlow',0x610:'Xhigh',0x611:'Y',0x612:'Yhigh',0x615:'facing',0x616:'action',0x617:'frame',0x618:'mode',0x4e1:'Yfraction',0x4e2:'Yvelocity',0x6c6:'fall_age'}
 original=P.T.NesMPU.step;rows={};modes=Counter();frame=900
 def step(cpu):
  m=cpu.memory;pc=cpu.pc;bank=7 if pc>=0xc000 else m.bank;before=tuple(m[a]for a in names);state=list(m[0x60e:0x619]);result=original(cpu)
  for (at,name),old,new in zip(names.items(),before,[m[a]for a in names]):
   if old==new:continue
   key=f'{bank}:{pc:04X}:{name}';q=rows.setdefault(key,dict(bank=bank,PC=hex(pc),field=name,writes=0,examples=[]));q['writes']+=1
   if len(q['examples'])<3:q['examples'].append(dict(physical_CPU_frame=frame,before=old,after=new,actor_before=state,actor_after=list(m[0x60e:0x619])))
   if name=='mode':modes[f'{old}->{new}']+=1
  return result
 P.T.NesMPU.step=step
 segments=[(150,1),(45,129),(50,0),(45,8),(90,65),(120,2),(45,130),(80,0),(45,10)]
 try:
  for count,pad in segments:
   for _ in range(count):P.frame(c,pad);frame+=1
 finally:P.T.NesMPU.step=original
 q=dict(passed=True,donor_sha256=P.SHA,source_CPU_only=True,native_host=False,natural_startup_frames=900,observed_active_frames=frame-900,mode_transitions=dict(modes),actual_original_writer_sites=list(rows.values()),scope='Genuine reset/menu/controller source flow. Actor writer instructions are observed directly, with bounded first examples; no source outcome or host RAM seeding. Used to distinguish script motion from original post-physics contact/progression not yet recovered.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),Path(P.__file__)]})
 (O/'actor-writer-authority.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['actual_original_writer_sites','bindings']}));print(json.dumps([v for v in rows.values()if v['field']in['mode','Y']]))


if __name__=='__main__':main()
