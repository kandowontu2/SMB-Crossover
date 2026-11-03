"""Actual GameLoop contact/pit death and native screen/respawn progression."""
from collections import Counter,deque
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_core_1102_v79 as C
import check_prince_native_stack_1102_v72 as S
N,O=S.N,C.O;address,location=S.address,S.location


def main():
 actual=N.NesMPU;events=Counter();points={};recent=deque(maxlen=16);epoch=0;case=None;rows=[];summaries=[]
 class Trace(actual):
  def step(self):
   m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None;name=points.get((self.pc,tag))
   if name:events[name]+=1;rows.append(dict(case=case,epoch=epoch,event=name,SP=self.sp,engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives')))
   recent.append((self.pc,self.sp,tag));return super().step()
 try:
  for case in ['contact','pit']:
   b,m,lab=C.loaded();version_witness=bytes(m.ram[2][0x766:0x780]);points.clear();events.clear()
   for name in ['KillPlayer','PlayerLoseLife','MegaManDeathUpdate','InitializeArea','SecondaryGameSetup']:
    points[address(b,name),((location(b,name)-16)//8192)|128]=name
   points[lab['PpNativeInit'],2]='PrinceInit';points[lab['PpNativeRetire'],2]='PrinceRetire'
   for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
   if case=='contact':S.fatal(m,b)
   else:S.C.C.terrain(m,lambda x,y:0x54 if x<96 and y>=208 else 0)
   N.NesMPU=Trace;minimum=224;life_epoch=None;resumed=None;maxx=48
   for epoch in range(1800):
    pad=1 if case=='pit'and life_epoch is None or resumed is not None else 0
    m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
    out=N.invoke(m,'GameLoop',a=83,x=0,y=0,p=0x21);minimum=min(minimum,out['minimum_SP'])
    engine=N.get(m,'GameEngineSubroutine');lives=N.get(m,'NumberofLives');x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');maxx=max(maxx,x)
    if lives==1 and life_epoch is None:life_epoch=epoch
    assert lives>=1,('Second unintended life loss',case,epoch)
    assert bytes(m.ram[2][0x766:0x780])==version_witness,('Old cold image reloaded; complete changed manager rebind required',case,epoch)
    if life_epoch is not None and engine==8 and N.get(m,'OperMode_Task')==3 and m.ram[2][0xab]==0xa7 and m.ram[2][0xac]==0 and m.ram[2][0x6cf]==5:
     if resumed is None:resumed=(epoch,x)
     elif x>=resumed[1]+16:break
    N.consume(m)
   else:raise AssertionError(('No controlled native respawn',case,engine,lives,life_epoch,resumed,m.ram[2][0xab:0xad].hex()))
   assert events['KillPlayer']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None
   summaries.append(dict(case=case,updates=epoch+1,life_decrement_epoch=life_epoch,resumed_epoch=resumed[0],resumed_x=resumed[1],final_x=x,final_engine=engine,final_lives=lives,sourceHP=m.ram[2][0x6cf],minimum_SP=minimum,actual_calls=dict(events)))
 except Exception as error:
  q=dict(passed=False,CPU_only=True,exception=repr(error),case=case,epoch=epoch,actual_calls=dict(events),events=rows,recent_instructions=list(recent))
  if 'm'in locals():q.update(engine=N.get(m,'GameEngineSubroutine'),task=N.get(m,'OperMode_Task'),lives=N.get(m,'NumberofLives'),ready=m.ram[2][0xab],pending=m.ram[2][0xac])
  (O/'post-return-respawn-negative-v93.json').write_text(json.dumps(q,indent=2)+'\n');raise
 finally:N.NesMPU=actual
 q=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected_after_old_authenticated_cold=True,changed_full_cold_manager_not_qualified=True,scenarios=summaries,events=rows,scope='Actual GameLoop and ordinary NMI drain, original source contact/pit, genuine native Kill/death/life/screen/respawn and resumed Right. Explicit CPU terrain/enemy/timer/input fixture only; no engine/death-age/life outcome seeds. Source code was injected after old authenticated cold, not current9cf image admission.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'native-stack-CPU-v89.json',O/'post-return-cold-CPU-v90.json']})
 (O/'post-return-respawn-CPU-v93.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['events','bindings']}))


if __name__=='__main__':main()
