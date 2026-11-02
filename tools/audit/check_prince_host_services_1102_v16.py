"""Actual6502 owner/epoch admission and genuine native pit-death fixtures."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_host_lifecycle_model_1102_v12 as C
O,W=C.O,C.W;N=W.N


def host(b):
 h=C.World(b);labels=C.P.T.labels(O/'host-services-v16.lbl');h.lab.update(labels)
 code=(O/'host-services-v16.bin').read_bytes();h.s[0x1b9a:0x1b9a+len(code)]=code
 N.put(h.m,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,NumberofLives=2)
 h.source('PpNativeInit');return h


def call(h,name):
 r0=W.address(h.b,'R0');zp=bytes(h.m[r0:r0+8]);smc=bytes(h.m[0x15a:0x17b]);maps=h.m.rawtags[:]
 c=h.source(name)
 assert bytes(h.m[r0:r0+8])==zp and bytes(h.m[0x15a:0x17b])==smc,(name,'foreground R0..R7/SMC changed')
 assert h.m.rawtags==maps
 return c


def main():
 b=W.scoped_load(C.BASE);h=host(b);h.terrain(lambda x,y:0x54 if y>=208 else 0)
 rejected=0
 for field,values in [('SelectedCharacter',[i for i in range(40)if i!=38]),('OperMode',[0,2,3]),('GameEngineSubroutine',[i for i in range(16)if i!=8]),('GamePauseStatus',[1,3,255])]:
  good=N.get(h.m,field)
  for value in values:
   N.put(h.m,**{field:value});before=[bytes(x)for x in h.m.ram];c=call(h,'PpNativeTick')
   assert not c.p&1 and before==[bytes(x)for x in h.m.ram],(field,value);rejected+=1
  N.put(h.m,**{field:good})
 for at,values in [(0xab,[0,1,166,168,255]),(0xac,[1,255])]:
  old=h.s[at]
  for v in values:
   h.s[at]=v;before=bytes(h.s);c=call(h,'PpNativeTick');assert not c.p&1 and bytes(h.s)==before;rejected+=1
  h.s[at]=old
 phases=[];duplicates=0
 for epoch in range(520):
  N.put(h.m,FrameCounter=epoch&255,SavedJoypad1Bits=1)
  prior=h.s[0xa6];c=call(h,'PpNativeTick');assert c.p&1 and h.s[0xa6]==(prior+1)&255
  phases.append((h.s[0xa6]-1)&3)
  before=[bytes(x)for x in h.m.ram];c=call(h,'PpNativeTick');assert not c.p&1 and before==[bytes(x)for x in h.m.ram];duplicates+=1
 assert phases==[i%4 for i in range(520)]
 phase=h.s[0xa6];N.put(h.m,GamePauseStatus=1,FrameCounter=77);assert not call(h,'PpNativeTick').p&1 and h.s[0xa6]==phase
 N.put(h.m,GamePauseStatus=0);assert call(h,'PpNativeTick').p&1 and h.s[0xa6]==(phase+1)&255
 # Full foreign retirement is still resident-owned; the private leaf makes
 # its local ready/epoch marker unusable immediately and cannot reenter.
 call(h,'PpNativeRetire');before=bytes(h.s);assert not call(h,'PpNativeTick').p&1 and bytes(h.s)==before
 pit_boundaries=[]
 for high,y,expect in [(0,0,False),(0,255,False),(1,0,False),(1,239,False),(1,240,True),(1,255,True),(2,0,True),(2,200,True)]:
  z=host(b);N.put(z.m,Player_Y_HighPos=high,Player_Y_Position=y)
  z.m.ram_writes=[];c=call(z,'PpNativePitDeath');dead=N.get(z.m,'GameEngineSubroutine')==11
  assert bool(c.p&1)==dead==expect and z.s[0xac]==int(expect),(high,y,dead)
  if expect:
   before=[bytes(a)for a in z.m.ram];assert not call(z,'PpNativePitDeath').p&1
   assert before==[bytes(a)for a in z.m.ram]and N.get(z.m,'NumberofLives')==2
  pit_boundaries.append(dict(YHigh=high,Y=y,death=dead,CPU=c.processorCycles))
 # Controller-only compact world: run off authored fixture ground, execute
 # original falling and native export, and invoke real KillPlayer before wrap.
 z=host(b);z.terrain(lambda x,y:0x54 if x<128 and y>=208 else 0);trace=[]
 for epoch in range(900):
  N.put(z.m,FrameCounter=epoch&255,SavedJoypad1Bits=1);c=call(z,'PpNativeTick')
  if epoch%20==0:trace.append(dict(epoch=epoch,X=N.get(z.m,'Player_X_Position')+256*N.get(z.m,'Player_PageLoc'),Y=N.get(z.m,'Player_Y_Position'),YHigh=N.get(z.m,'Player_Y_HighPos'),sourceY=z.s[0x611],sourceMode=z.s[0x618]))
  if N.get(z.m,'GameEngineSubroutine')==11:break
 else:raise AssertionError(('Genuine source fall/native death not reached',trace[-1]))
 assert z.s[0xac]==1 and N.get(z.m,'NumberofLives')==2
 # Native death progression/respawn needs the eventual resident scene hook;
 # this fixture proves actual KillPlayer ingress, not later Main lifecycle.
 q=dict(passed=True,private_CPU_only=True,native_emulator=False,host_ROM_created=False,base_ROM_SHA256=C.PIN,negative_owner_scene_pause_ready_cases=rejected,consecutive_epoch_updates=520,duplicate_epoch_calls_rejected=duplicates,epoch_wraps=2,source_phase_order=[0,1,2,3],pause_reentry_same_epoch=True,local_retirement_blocks_reentry=True,pit_boundaries=pit_boundaries,original_run_then_fall=dict(Main_updates=epoch+1,engine=N.get(z.m,'GameEngineSubroutine'),lives=N.get(z.m,'NumberofLives'),trace=trace),native_R0_R7_SMC_mapper_preserved=True,source_audio_remains_explicit_fixture=True,scope='Exact installed1966 native fields and real KillPlayer/FarCallCommon execute. Native export/death intentionally change their declared native player/state fields. Private leaves require resident authentication before entry. This does not qualify shared owner/header/cold/retirement integration, native Main respawn, audio, combat, emulator, full1-1 or helper crossing.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'host-services-v16.bin',O/'host-services-layout-v16.json',O/'host-life-v12.bin',O/'host-life-CPU-v12.json',R/'src/game.s',C.BASE]})
 (O/'host-services-CPU-v16.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','pit_boundaries','original_run_then_fall']}));print(json.dumps(q['original_run_then_fall']))


if __name__=='__main__':main()
