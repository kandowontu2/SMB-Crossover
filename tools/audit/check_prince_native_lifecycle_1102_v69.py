"""Actual original contact/death animation/native GameRoutines/life progression."""
from collections import Counter,deque
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_player_pipeline_1102_v67 as C
M,N,O=C.M,C.N,C.O;address,location=C.address,C.location


def main():
 b,m,lab=C.loaded();C.terrain(m,lambda x,y:0x54 if y>=208 else 0);N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21);N.put(m,ObjectOffset=0)
 for field,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,Enemy_MovingDir=2).items():m[address(b,field)]=value
 for native in ['RelativeEnemyPosition','GetEnemyOffscreenBits','GetEnemyBoundBox']:N.invoke(m,native,a=83,x=0,y=0,p=0x21)
 N.invoke(m,'PlayerEnemyCollision',a=83,x=0,y=0,p=0x21);assert m.ram[2][0x6cf]==0 and m.ram[2][0x616]==85 and N.get(m,'GameEngineSubroutine')==8
 # The admitted overlap caused the genuine original fatal source reaction.
 # Retire only this explicit CPU enemy fixture after the single contact;
 # subsequent source/native death advancement uses the actual engine tree.
 m[address(b,'Enemy_Flag')]=0
 actual=N.NesMPU;tags=Counter();calls=Counter();points={};recent=deque(maxlen=64)
 for name in ['KillPlayer','PlayerDeath','PlayerLoseLife','MegaManDeathUpdate']:
  pc=address(b,name);points[pc,((location(b,name)-16)//8192)|128]=name
 class Trace(actual):
  def step(self):
   recent.append(dict(PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,op=self.memory[self.pc],maps=self.memory.rawtags[:]))
   if self.pc>=0x8000:
    tag=self.memory.rawtags[(self.pc-0x8000)//8192];name=points.get((self.pc,tag))
    if name:calls[name]+=1
    if self.pc==lab['PpNativeRoute']and tag==2:tags[self.memory.ram[2][0x9e]]+=1
   return super().step()
 N.NesMPU=Trace;rows=[];minimum=224;first_death=None
 try:
  for epoch in range(600):
   N.put(m,FrameCounter=epoch&255,SavedJoypad1Bits=0,SavedJoypadBits=0);out=N.invoke(m,'GameRoutines',a=83,x=0,y=0,p=0x21);minimum=min(minimum,out['minimum_SP']);engine=N.get(m,'GameEngineSubroutine')
   if engine==11 and first_death is None:first_death=epoch
   if epoch%20==0 or N.get(m,'NumberofLives')<2:rows.append(dict(epoch=epoch,engine=engine,lives=N.get(m,'NumberofLives'),HP=m.ram[2][0x6cf],source_pose=m.ram[2][0x617],source_dead=m.ram[2][0xac],source_phase=m.ram[2][0xa6],native_death_age=N.get(m,'MmDeathAge')))
   if N.get(m,'NumberofLives')<2:break
 except Exception as error:
  q=dict(passed=False,CPU_only=True,base_SHA256=M.PIN,memory_SHA256=M.sha(b['raw']),exception=str(error),epoch=epoch,engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),pose=m.ram[2][0x617],source_dead=m.ram[2][0xac],calls=dict(calls),tags=dict(tags),trace=rows,recent_instructions=list(recent));(O/'native-lifecycle-negative-v69.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['trace','recent_instructions']}));raise
 finally:N.NesMPU=actual
 passed=N.get(m,'NumberofLives')==1 and calls['KillPlayer']==1 and calls['PlayerLoseLife']==1
 q=dict(passed=passed,CPU_only=True,ROM_written=False,native_emulator=False,base_SHA256=M.PIN,memory_SHA256=M.sha(b['raw']),initial_lives=2,final_lives=N.get(m,'NumberofLives'),updates=epoch+1,first_native_death_epoch=first_death,final_engine=N.get(m,'GameEngineSubroutine'),actual_native_calls=dict(calls),actual_public_tags=dict(tags),minimum_SP=minimum,trace=rows,scope='Actual native enemy overlap causes authentic source fatal contact/action85, actual GameRoutines advances original death pose185 then genuine KillPlayer. Continue the actual native engine for600epochs or life decrement; no native death age/timer/engine outcome writes. Explicit CPU enemy/metatiles only, no emulator RAM seed/native fullstage/respawn claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-manifest-v65.json',O/'native-ingress-CPU-v66.json',O/'player-pipeline-CPU-v67.json']})
 (O/('native-lifecycle-CPU-v69.json'if passed else'native-lifecycle-negative-v69.json')).write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['trace','bindings']}));assert passed,'Actual complete death progression failed; negative retained.'


if __name__=='__main__':main()
