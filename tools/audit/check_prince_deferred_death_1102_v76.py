"""Actual GameCore same-epoch queue/delivery/life CPU experiment, no admission."""
from collections import Counter,deque
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_native_lifecycle_1102_v71 as C
import check_prince_native_stack_1102_v72 as S
import measure_prince_collision_services_1102_v49 as A
O=C.O;N=C.C.N;address,location=C.C.address,C.C.location


def loaded():
 b,m,_=C.original_loaded();runtime=(O/'native-runtime-v75.bin').read_bytes();metadata=(O/'native-metadata-v75.bin').read_bytes();audio=(O/'native-state-v75.bin').read_bytes()[-154:]
 m.ram[3][:len(runtime)]=runtime;m.ram[2][0x800:0x800+len(metadata)]=metadata;m.ram[2][0x766:0x800]=audio
 lab=json.loads((O/'native-labels-v75.json').read_text())
 text=(O/'collision-selector-v59.s').read_text().replace('PpNativeRoute=$df26',f'PpNativeRoute=${lab["PpNativeRoute"]:04x}')
 blob,_=A.A.assemble('deferred-selector-v76',text,(O/'collision-selector-v59.cfg').read_text());raw=bytearray(b['raw']);at=16+65*8192+0x740;raw[at:at+len(blob)]=blob;m.bundle=dict(b,raw=bytes(raw))
 for win,tag in enumerate(m.rawtags):
  if tag==193:m.raw_page(win,tag)
 N.put(m,Mirror_PPUMASK=30);m[0x2001]=30
 return b,m,lab


def main():
 b,m,lab=loaded();S.fatal(m,b)
 # A regular live native timer is part of this explicit CPU world fixture;
 # no death age, death timer, engine transition or life outcome is written.
 for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
 actual=N.NesMPU;calls=Counter();events=[];recent=deque(maxlen=32);epoch=0;last_dead=m.ram[2][0xac];points={}
 for name in ['KillPlayer','PlayerDeath','PlayerLoseLife','MegaManDeathUpdate','GameRoutines','NrObjectWeaponTail','PlayerGfxHandler','GuestPostEnemyCollision']:
  points[address(b,name),((location(b,name)-16)//8192)|128]=name
 points[lab['PpNativeDeferredKill'],2]='PpNativeDeferredKill'
 class Trace(actual):
  def step(self):
   nonlocal last_dead
   bank=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None;name=points.get((self.pc,bank))
   recent.append(dict(PC=self.pc,SP=self.sp,bank=bank))
   if name:calls[name]+=1;events.append(dict(epoch=epoch,event=name,SP=self.sp,dead=self.memory.ram[2][0xac],engine=N.get(self.memory,'GameEngineSubroutine')))
   dead=self.memory.ram[2][0xac]
   if dead!=last_dead:events.append(dict(epoch=epoch,event='source_pending_change',old=last_dead,new=dead,SP=self.sp));last_dead=dead
   return super().step()
 N.NesMPU=Trace;rows=[];minimum=224;first_death=None
 try:
  for epoch in range(260):
   N.put(m,FrameCounter=epoch&255,SavedJoypad1Bits=0,SavedJoypadBits=0)
   out=N.invoke(m,'GameCoreRoutine',a=83,x=0,y=0,p=0x21);minimum=min(minimum,out['minimum_SP'])
   engine=N.get(m,'GameEngineSubroutine')
   if engine==11 and first_death is None:first_death=epoch
   if epoch%20==0 or N.get(m,'NumberofLives')<2:rows.append(dict(epoch=epoch,engine=engine,lives=N.get(m,'NumberofLives'),HP=m.ram[2][0x6cf],pose=m.ram[2][0x617],pending=m.ram[2][0xac],death_age=N.get(m,'MmDeathAge')))
   if N.get(m,'NumberofLives')<2:break
 except Exception as error:
  (O/'deferred-death-negative-v76.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_code_injected=True,exception=repr(error),epoch=epoch,calls=dict(calls),events=events,trace=rows,recent_instructions=list(recent)),indent=2)+'\n');raise
 finally:N.NesMPU=actual
 passed=N.get(m,'NumberofLives')==1 and calls['KillPlayer']==1 and calls['PlayerLoseLife']==1 and first_death==20
 q=dict(passed=passed,CPU_only=True,source_code_injected=True,qualified_cold=False,ROM_written=False,minimum_SP=minimum,updates=epoch+1,first_native_death_epoch=first_death,final_lives=N.get(m,'NumberofLives'),native_calls=dict(calls),events=events,trace=rows,scope='Actual complete GameCoreRoutine returns from original/native movement, then services earned Prince death request on actual row34 before enemies/draw in the same Main epoch. Genuine native Kill/UnionDeathStart/death update/life routines are unmodified. Explicit CPU native enemy/metatile/timer fixtures; no emulator RAM outcome seeding or admitted component/cold/IRQ/fullstage claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'deferred-death-measurement-v75.json',O/'native-runtime-v75.bin',O/'native-metadata-v75.bin',O/'native-state-v75.bin',O/'deferred-selector-v76.bin']})
 (O/('deferred-death-CPU-v76.json'if passed else'deferred-death-negative-v76.json')).write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','events','trace']}));assert passed


if __name__=='__main__':main()
