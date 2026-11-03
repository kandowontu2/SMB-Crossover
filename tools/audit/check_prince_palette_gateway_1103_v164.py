"""Real whole native pickups with the new kind0 palette gateway."""
from pathlib import Path
from collections import Counter
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
N,O,I=V.N,V.O,V.I


def main():
 base,seed,lab=V.loaded();N.put(seed,TimerControl=1);N.invoke(seed,'HuFullBox',a=83,x=0,y=0,p=0x21);actual=N.NesMPU;calls=Counter();pending=None;entries=[]
 class Trace(actual):
  def step(self):
   nonlocal pending
   tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
   if pending is not None and(self.pc,self.sp)==pending:pending=None
   if self.pc==lab['PpNativeCall']and tag==2:
    entries.append(dict(kind=self.y,SP=self.sp,pending=pending))
    assert pending is None,('NativeCall packet reentry',entries)
    pending=(((self.memory[0x101+self.sp]|self.memory[0x102+self.sp]<<8)+1)&65535,self.sp+2)
    calls[self.y]+=1
   return super().step()
 N.NesMPU=Trace;rows=[]
 try:
  for kind in range(4):
   m=N.fork(seed);m.ram[2][0x6cf]=4;slot=5;N.put(m,ObjectOffset=slot)
   for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=183,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[I.address(base,name)+slot]=value
   before=dict(calls);out=N.invoke(m,'PowerUpObjHandler',a=83,x=slot,y=0,p=0x21);assert pending is None and not m[I.address(base,'Enemy_Flag')+slot]and N.get(m,'NumberofLives')==2
   if kind==0:assert m.ram[2][0x6cf]==5
   elif kind==1:assert m.ram[2][0x6ee]==1 and m.ram[2][0x616]==91
   elif kind==2:assert N.get(m,'StarInvincibleTimer')==35
   else:assert m[I.address(base,'FloateyNum_Control')+slot]==11
   rows.append(dict(kind=kind,minSP=out['minimum_SP'],gateway={k:v-before.get(k,0)for k,v in calls.items()if v!=before.get(k,0)}))
 finally:N.NesMPU=actual
 q=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,whole_native_PowerUpObjHandler=rows,gateway_entries=entries,no_synchronous_packet_reentry=True,scope='Actual159 sourcebacked fullcold, complete native item movement/maturity/rectangle/collision/collector. Every reached NativeCall observes no live gateway packet. Real native outcomes asserted; actor/type/sourceHP inputs are isolated CPU fixture preconditions. No emulator/outcome seeds/native-playable claim.',bindings={p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'backdrop-manifest-v159.json']})
 (O/'palette-gateway-CPU-v164.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'palette-gateway-negative-v164.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
