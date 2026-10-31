"""Real vector cuts at each new owner/scene/load/fallback instruction."""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_cold_warm_retirement_controls_v1 as V
import contra_force_loader_isr_controls_v2 as U
T,C=V.T,V.C;J=V.J
O=R/'build/cf-cold-warm-hook-isr-controls-v2'
sha=V.sha

def ready(raw=0,loaded=False):
 V.select(J);U.B=T.B
 m=V.V.loaded(J,0)if loaded else T.Bus()
 T.put(m,SelectedCharacter=raw,FmGroups=0,FmAlts=0,OperMode=1,OperMode_Task=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,CurrentPlayer=0,GamePauseStatus=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,NumberofLives=2)
 m[T.address(T.B,'VRAM_Buffer1')]=0
 m.writes.clear();m.ram_writes.clear();m.executed_guest.clear();return m

def start(m,n,p=0x30):return C.start(m,T.address(T.B,n),(T.location(T.B,n)-16)//8192|128,a=0x57,x=0xa9,y=0x63,p=p)

def spans():
 out=[]
 for n,size in [('CfSceneRetireForeign',17),('CfLoadIfCold',42),('BwResolveColdNative',14),('BwCfSceneLoad',37),('BtRouter',24)]:
  pc=T.address(T.B,n);raw=(T.location(T.B,n)-16)//8192|128;out.append((raw,pc,pc+size,n))
 return out

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,vectors=[],paths=[])
 try:
  V.select(J);U.B=T.B;owned=spans()
  # Accepted transfer paths are legal lag-NMI contexts. Ordinary and
  # paused normal NMIs use raw0 foreign scene or an invalid direct row;
  # no fixture forces NmiDisable negative after an ordinary poll.
  paths=[('foreign_scene','BwScene',0,False,255,0),('foreign_normal','BwScene',0,False,0,0),('foreign_paused','BwScene',0,False,0,1),('CF_cold','BwScene',31,False,255,0),('CF_warm','BwScene',31,True,255,0)]
  paths += [(f'fallback_{s}_{lag}_{pause}','BtServiceVeneers',31,False,lag,pause,s)for s in[15,19]for lag,pause in[(0,0),(0,1),(255,0)]]
  for row in paths:
   label,n,raw,loaded,lag,pause,*service=row;m=ready(raw,loaded);T.put(m,NmiDisable=lag,GamePauseStatus=pause)
   # Stable title foreign contexts avoid inventing an uninitialized native
   # music session. Accepted CF scenes remain genuine mode1 forcedblank.
   if raw==0 or(service and lag==0):T.put(m,OperMode=0)
   c=start(m,n)
   if service:
    m[T.address(T.B,'FarcallJmpTarget_SMC')+1]=(T.address(T.B,n)+3*service[0])&255
    m[T.address(T.B,'FarcallJmpTarget_SMC')+2]=(T.address(T.B,n)+3*service[0])>>8
   seen=set();steps=0;low=c.sp;newpoints=[]
   while c.pc!=0x7fff:
    pc=c.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    match=next((name for bank,lo,hi,name in owned if tag==bank and lo<=pc<hi),None)
    # Include only the new private-frame seams; already-qualified full
    # 24KB transfer cuts are bound separately rather than duplicated here.
    if match and(tag,pc)not in seen:
     seen.add((tag,pc));newpoints.append([tag,pc,match])
     for kind in['NMI','IRQ']:
      if kind=='IRQ'and c.p&4:continue
      mem,cpu=U.clone(m,c);mem[0x5204]=128
      proof=U.interrupt(mem,cpu,kind,keep_ppu=False)
      assert U.state(cpu)==U.state(c)
      q['vectors'].append(dict(path=label,PC=pc,raw=tag,owner=match,sourceSP=c.sp,**proof))
    low=min(low,c.sp);c.step();steps+=1;assert steps<900000,(label,hex(c.pc))
   assert c.sp==224
   if label.startswith('CF_'):
    assert m.ram[2][0x1fe0]==167 and m.ram[2][0x2e1]==1
   q['paths'].append(dict(path=label,CPU=c.processorCycles,steps=steps,minimum_SP=low,new_instruction_points=newpoints))
  assert all(any(r['owner']==n for r in q['vectors'])for n in['CfSceneRetireForeign','CfLoadIfCold','BwResolveColdNative','BwCfSceneLoad','BtRouter'])
  q['retained_v1_negative']='V1 used poisoned loader API native audio state with raw0/mode1; actual legacy audio legitimately updated MusicData DA/DB. V2 uses stable genuine title mode0 for foreign normal/paused contexts. No vector assertion relaxed and no source change.'
  q.update(passed=True,real_vector_cases=len(q['vectors']),minimum_ISR_SP=min(r['minimum_SP']for r in q['vectors']),scope='Immediate real vector return at every reached new helper/gate/fallback instruction, all33SMC/livepage1/R0..7/rawmaps/4WRAM preserved. Original foreground then completes once per real path. Accepted copies use lag contexts; full transfer seams and callback continuation are independently bound. No native/readiness/palette claim.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 paths=[Path(__file__),R/'tools/audit/cf_cold_warm_hook_isr_controls_v1.py',R/'build/cf-cold-warm-hook-isr-controls-v1/controls.json',Path(V.__file__),Path(U.__file__),Path(T.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'cf-stream.bin',J/'cf-cookie.bin',R/'build/contra-force-cold-warm-rebind-isr-v1/controls.json',R/'build/contra-force-checkpoint-loader-qualified-v1/handoff.json']
 q['bindings']={str(p.resolve()):sha(p)for p in paths};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['vectors','paths','bindings']}));assert q['passed']
if __name__=='__main__':main()
