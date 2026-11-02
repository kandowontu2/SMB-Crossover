"""Actual native secondary-actor lifecycle; private CPU cartridge only."""
import json
from pathlib import Path
import check_bubble_bobble_native_policy_1102_v4 as Q
P=Q.P;C=Q.C;N=Q.N;O=P.O;R=P.R;address=Q.address


def bundle(ports=True):
 b,prior,route,_=Q.bundle();q=json.loads((O/'native-proxy-layout.json').read_text())
 parts=[(65,0xae00,'native-proxy-owner.bin'),(65,0xa740,'native-proxy-routes.bin'),(65,0xb013,'native-proxy-route-scene-gate.bin'),(65,0xb026,'native-proxy-route-retire-stub.bin'),(65,0xb029,'native-proxy-typed-contact.bin'),(65,0xb031,'native-proxy-route-foreign.bin'),(65,0xb062,'native-proxy-route-scene-own.bin'),(74,0xbf03,'native-proxy-contact-gate.bin')]
 if ports:parts +=[(65,0xadb6,'native-proxy-ports.bin'),(65,0xadd8,'native-proxy-bbox.bin')]
 b=C.patched(b,[(bank,pc,(O/name).read_bytes())for bank,pc,name in parts]);raw=bytearray(b['raw']);image=(O/'native-proxy.bin').read_bytes()
 for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 raw[1048592+441*1024:1048592+442*1024]=(O/'native-proxy-helper.chr').read_bytes()
 if ports:
  at=16+77*8192+0xb09;old=bytes.fromhex('8d6a01a9d78d6c01a9ad8d6d01a9c14c5a01');assert raw[at:at+18]==old;raw[at+4]=0xd8
 b['raw']=bytes(raw);return b,q,route


def fresh(b,route,identity=0):
 return Q.fresh(b,route,identity)


def update(m,frame,keys=0):
 N.put(m,FrameCounter=frame&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12)
 return N.invoke(m,'HuMovement',a=85,x=0,y=0,p=0x31)


def native_enemy(m,slot):
 N.put(m,ObjectOffset=slot);return N.invoke(m,'EnemiesAndLoopsCore',x=slot,y=0,p=0x31)


def fields(m,slot):
 return {n:N.get(m,n,slot)for n in['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']}


def trap(b,route,identity=0,slot=0,run_native=True):
 m=fresh(b,route,identity);Q.enemy(m,x=100,y=184,slot=slot);N.put(m,ObjectOffset=slot,TimerControl=0)
 # The normal native birth sets its real16px bbox and enemy state. This is
 # an explicit legal arena placement, not an assertion of parser/controller ingress.
 N.invoke(m,'InitGoomba',x=slot);m[address(b,'Enemy_X_Speed')+slot]=8
 saved=fields(m,slot)
 for frame in range(40):
  update(m,frame,64 if frame==0 else 0)
  if m.ram[2][0x320+16*slot]:
   assert N.get(m,'Enemy_Flag',slot)==0x80|slot,(identity,slot,frame,fields(m,slot))
   return m,frame,saved
  if run_native:native_enemy(m,slot)
 raise AssertionError(('Original shot failed to trap',identity,slot,fields(m,slot),list(m.ram[2][0x68:0x80])))


def main():
 b,q,route=bundle();checks={};native=N.NesMPU;counts={}
 names=['EnemiesAndLoopsCore','RunEnemyObjectsCore','EnemyMovementSubs','PlayerEnemyCollision','EnemyGraphicsEngine','DrawAllMetasprites','DrawMetasprite','ShellOrBlockDefeat','CheckpointEnemyID']
 points={(((Q.Q.location(b,n)-16)//8192)|128,address(b,n)):n for n in names if n in b['syms']}
 class Trace(native):
  def step(self):
   if self.pc>=0x8000:
    n=points.get((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc))
    if n:counts[n]=counts.get(n,0)+1
   return native.step(self)
 N.NesMPU=Trace
 try:
  timed=[];popped=[];retired=[];birth=[];art=[]
  for identity in[0,1]:
   m,frame,saved=trap(b,route,identity);assert counts.get('EnemyGraphicsEngine',0)>0
   pose=N.get(m,'EnemyMetasprite');assert pose>0
   before=fields(m,0);before_counts=dict(counts)
   for _ in range(5):native_enemy(m,0)
   assert fields(m,0)==before and N.get(m,'EnemyMetasprite')==pose
   assert counts.get('RunEnemyObjectsCore',0)==before_counts.get('RunEnemyObjectsCore',0)and counts.get('PlayerEnemyCollision',0)==before_counts.get('PlayerEnemyCollision',0)
   # Actual native object renderer retains and consumes the captured pose;
   # no Python DrawMetasprite/EnemyGraphics callback supplies its art.
   N.put(m,CurrentOAMOffset=24,GuestOamRotationActive=0,RgOamUsed=24,VRAM_Buffer1_Offset=0)
   m[512:768]=[248,0,0,0]*64
   before_draw=counts.get('DrawMetasprite',0);N.invoke(m,'DrawAllMetasprites')
   assert counts.get('DrawMetasprite',0)>before_draw and N.get(m,'EnemyMetasprite')==pose
   records=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240]
   assert records and N.get(m,'CurrentOAMOffset')%4==0,(identity,records)
   art.append(dict(identity=identity,pose=pose,native_records=len(records),native_DrawMetasprite_calls=counts['DrawMetasprite']-before_draw))
   # The original stage1/rank7 trap deadline is40 source updates. Move the
   # source player away through native coordinates to avoid a legitimate pop.
   N.put(m,Player_X_Position=32);start_timer=m.ram[2][0x213];defeats=counts.get('ShellOrBlockDefeat',0)
   for epoch in range(frame+1,frame+65):
    update(m,epoch);native_enemy(m,0)
    if not m.ram[2][0x320]:break
   assert not m.ram[2][0x320]and N.get(m,'Enemy_Flag')==saved['Enemy_Flag']and counts.get('ShellOrBlockDefeat',0)==defeats
   assert counts.get('EnemyMovementSubs',0)>before_counts.get('EnemyMovementSubs',0)
   timed.append(dict(identity=identity,trap_frame=frame,timer_at_capture=start_timer,release_epoch=epoch,flag=N.get(m,'Enemy_Flag'),native_AI_resumed=True))
   # Genuine original contact/pop restores the positive flag before entering
   # native defeat; subsequent source updates cannot award a second credit.
   m,frame,saved=trap(b,route,identity);N.put(m,Player_X_Position=N.get(m,'Enemy_X_Position'),Player_PageLoc=N.get(m,'Enemy_PageLoc'),Player_Y_Position=(N.get(m,'Enemy_Y_Position')-8)&255,Player_Y_HighPos=1)
   before=counts.get('ShellOrBlockDefeat',0)
   for epoch in range(frame+1,frame+10):update(m,epoch);native_enemy(m,0)
   assert counts.get('ShellOrBlockDefeat',0)==before+1 and N.get(m,'Enemy_Flag')==saved['Enemy_Flag']and N.get(m,'Enemy_State')&32
   popped.append(dict(identity=identity,native_defeat_calls=1,positive_flag=N.get(m,'Enemy_Flag')))
   # The real authenticated foreign-retirement seam restores all saved native
   # AI fields and flags before source cache/header invalidation.
   m,frame,saved=trap(b,route,identity);expected={k:v for k,v in saved.items()if k!='Enemy_ID'};N.put(m,SelectedCharacter=0)
   z=C.call(m,q['owner_labels']['CoRetire']);assert all(N.get(m,n)==v for n,v in expected.items()),(saved,fields(m,0),z)
   before=fields(m,0);C.call(m,q['owner_labels']['CoRetire']);assert fields(m,0)==before and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
   retired.append(dict(identity=identity,original_fields=expected,repeat_retire_unchanged=True))
   # Actual native frenzy publication + CheckpointEnemyID reuses the same
   # slot and ID positively. Source observe must discard its stale token,
   # without restoring old velocity or crediting the newly initialized actor.
   m,frame,saved=trap(b,route,identity);N.put(m,EnemyFrenzyQueue=6,ObjectOffset=0,Enemy_Y_Position=(N.get(m,'Enemy_Y_Position')-8)&255,WorldNumber=0,LevelNumber=0)
   before=counts.get('CheckpointEnemyID',0);N.invoke(m,'ChkEnemyFrenzy',x=0,p=0x30)
   assert counts.get('CheckpointEnemyID',0)>before and N.get(m,'Enemy_Flag')==1 and N.get(m,'Enemy_ID')==6
   newborn=fields(m,0);before=counts.get('ShellOrBlockDefeat',0)
   # The next genuine public movement update observes the positive native
   # publication before reconstructing a fresh, untrapped source proxy.
   update(m,frame+1)
   assert fields(m,0)==newborn and m.ram[2][0x320]==0 and not m.ram[2][0x6a]&16 and counts.get('ShellOrBlockDefeat',0)==before
   birth.append(dict(identity=identity,newborn_fields_retained=True,same_ID=6,positive_spawn=True))
  # Every native slot and positive flag boundary round-trips through the
  # authenticated retire seam exactly once. Positive non-one flags here are
  # explicit ABI fixtures; the genuine native birth above publishes one.
  exact=[]
  for slot,flag in enumerate([1,2,7,16,64,127]):
   m,frame,saved=trap(b,route,slot=slot);token=0x320+16*slot
   m.ram[2][token+2]=flag
   start=len(m.writes);N.put(m,SelectedCharacter=0);C.call(m,q['owner_labels']['CoRetire'])
   address_flag=address(b,'Enemy_Flag')+slot;first=sum(at==address_flag and value==flag for at,value in m.writes[start:])
   assert first==1 and N.get(m,'Enemy_Flag',slot)==flag and m.ram[2][token]==0,(slot,flag,first)
   start=len(m.writes);C.call(m,q['owner_labels']['CoRetire']);assert not any(at==address_flag for at,value in m.writes[start:])
   exact.append(dict(slot=slot,saved_positive_flag=flag,restore_writes=first,repeated_retire_flag_writes=0))
  checks.update(actual_native_suspension_and_retained_art=art,original_timeout_native_resume=timed,original_pop_native_defeat_once=popped,actual_authenticated_foreign_retirement=retired,actual_same_ID_native_spawn_invalidates=birth,all_six_native_slots_saved_flag_restored_once=exact)
 finally:N.NesMPU=native
 out=dict(passed=True,ROM_written=False,shared_source_written=False,admitted=False,base_ROM_SHA256=P.PIN,checks=checks,actual_native_calls=counts,layout=q,scope='Actual original source update plus native EnemiesAndLoopsCore/DrawAllMetasprites/defeat/retire/spawn routines in explicit legal arena fixtures. No new shared AI/birth hook and no Python victim-art or actor-birth orchestration. Complete Main/foreign service/ports/IRQ/native controller qualification remains separate.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py',O/'native-proxy.bin',O/'native-proxy-helper.chr',O/'native-proxy-owner.bin',O/'native-proxy-typed-contact.bin',O/'native-proxy-contact-gate.bin',O/'native-proxy-ports.bin',O/'native-proxy-bbox.bin']})
 (O/'native-proxy-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,ROM_written=False)))


if __name__=='__main__':main()
