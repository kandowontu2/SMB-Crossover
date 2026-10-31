"""Private59B source factoring and own selected-C2 palette/API checks."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_runtime_controls_v3 as V
import ff_joint_native_flash_controls_1030_v3 as F
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address,location
from ff_wram_host_isr_v4 import clone
from wwf_first_hogan_owner_isr_v1 import interrupt
H=V.H;T=V.T
J=R/'build/wwf-hogan-natural-source-v15/joint';P=R/'build/contra-force-world-roles-1031-v2/joint'
O=R/'build/wwf-hogan-foreign-draw-controls-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
flags=[0x30|(n&15)|((n&48)<<2)for n in range(64)]

def own(b):
 V.J=J
 return V.make(b)

def shared(m,p=0x71,hook=None):
 c=H.start(m,'FwNativeDrawAll',p=p);c,lo=H.finish(m,c,hook);assert m.rawtags[2]==H.get(m,'CurrentBankC');return c,lo

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,readiness=False,shared_private_proposal=True,checks={})
 old=T.qualified(P/'candidate.nes');b=T.qualified(J/'candidate.nes')
 try:
  # Actual emitted classifier: stop after original native State load.
  code=b['raw'][location(b,'FwNativeDrawAll'):location(b,'FwNativeDrawAll')+59]
  assert len(code)==59 and code[:9]==bytes([0xad,address(b,'SelectedCharacter')&255,address(b,'SelectedCharacter')>>8,0x49,31,0x29,253,0xf0,26])
  a=[0]*65536;a[0x4000:0x403b]=code;count=0
  for raw,p,state,acc in itertools.product(range(256),flags,[0,1,128,255],[0,87,255]):
   a[address(b,'SelectedCharacter')]=raw;a[address(b,'SmFreezeRenderState')]=state
   c=NesMPU(memory=a,pc=0x4000);c.a,c.x,c.y,c.p,c.sp=acc,169,99,p,224
   stop=0x4000+(38 if raw in[29,31]else 12)
   while c.pc!=stop:c.step()
   assert(c.a,c.x,c.y,c.sp)==(state,169,99,224)
   assert c.p==(p&125)|(state&128)|(2 if state==0 else 0)
   count+=1
  q['checks']['actual_classifier']=dict(passed=True,cases=count,selected_only=[29,31],all64flags=True,Carry_preserved=True)
  # Actual complete native callbacks, including the deliberate native carry.
  rows=[]
  for raw,freeze,p in itertools.product([0,2,9,22,27,31,32,33],[0,1],flags):
   if freeze and raw!=2:continue
   pair=[];cost=[];maps=[];calls=[]
   for bundle in [old,b]:
    m=F.seed(bundle,raw);H.put(m,SmFreezeRenderState=freeze,SpriteShuffleOffset=1)
    m[address(bundle,'ObjectMetasprite')+1]=F.enemy(m,0,12)
    m.writes.clear();m.ram_writes.clear();hit=[]
    def watch(mem,cpu,step):
     for n in ['DrawAllMetasprites','SamusFreezeRenderFinish']:
      if cpu.pc==address(bundle,n)and mem.rawtags[(cpu.pc-32768)//8192]==((location(bundle,n)-16)//8192)|128:hit.append(n)
    c,lo=shared(m,p,watch)
    pair.append(F.signature(m,c));cost.append(c.processorCycles)
    maps.append([(a,v)for a,v in m.writes if a in[0x5115,0x5116]])
    calls.append(hit)
   assert pair[0]==pair[1],('native outputs',raw,freeze,p)
   assert calls[0]==calls[1] and calls[0].count('DrawAllMetasprites')==1,(raw,freeze,p,calls)
   rows.append([raw,freeze,p,cost[1]-cost[0],len(maps[1])-len(maps[0])])
  q['checks']['genuine_foreign_CF_callbacks']=dict(passed=True,cases=len(rows),rows=rows,CPU_delta=[min(r[3]for r in rows),max(r[3]for r in rows)],once_order_native_outputs=True)
  q.update(passed=True,candidate=sha(J/'candidate.nes'))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(V.__file__),Path(F.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json',P/'candidate.nes',P/'candidate.dbg']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in ['passed','candidate','error']}))
if __name__=='__main__':main()
