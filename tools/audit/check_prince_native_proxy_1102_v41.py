"""In-memory original battle/native actor proxy episodes, no ROM or emulator."""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
import measure_prince_palette_contact_1102_v32 as Q
H,O,N=Q.H,Q.O,Q.N


def host(base):
 h=H.host(base);h.lab.update(H.P.T.labels(O/'native-proxy-v40.lbl'));h.lab.update(H.P.T.labels(O/'native-battle-v40.lbl'))
 for at,name in [(0x4400,'native-proxy-v40.bin'),(0x4000,'native-battle-v40.bin')]:
  blob=(O/name).read_bytes();h.m[at:at+len(blob)]=blob
 old=h.lab['PpControlComplete']
 for name,delta in [('PpN_7_F044',2),('PpN_7_F08D',3)]:
  at=h.lab[name]+delta;assert bytes(h.m[at:at+3])==bytes([0x4c,old&255,old>>8]);h.m[at+1:at+3]=h.lab['PpCombatControls'].to_bytes(2,'little')
 assert not h.callbacks
 # Settled-ground actor fixture. The separate first-controls negative has an
 # unset WorldSurface before phase3; preserve it rather than seeding a floor.
 for frame in range(8):
  N.put(h.m,FrameCounter=frame,SavedJoypad1Bits=0);h.source('PpNativeTick')
 assert h.s[0x7f]==208 and h.s[0x611]==128
 return h


def enemy(h,slot,x=80,ID=6,**values):
 fields=dict(Enemy_Flag=1,Enemy_ID=ID,Enemy_State=0,Enemy_BoundBoxCtrl=3,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2);fields.update(values)
 for name,value in fields.items():h.m[H.W.address(h.b,name)+slot]=value


def native(h,name,slot=0):return h.m[H.W.address(h.b,name)+slot]


def main():
 base,_,_,_=M.bundle();H.W.PIN=M.A.PIN;counts=Counter();cost=[];events=Counter();minimum=224
 defeat=H.W.address(base,'ShellOrBlockDefeat');bank=((H.W.location(base,'ShellOrBlockDefeat')-16)//8192)|128
 original=N.NesMPU
 class Trace(original):
  def step(self):
   if self.pc==defeat and self.memory.rawtags[1]==bank:events['actual_native_defeat']+=1
   return super().step()
 N.NesMPU=Trace
 try:
  # Explicit CPU fixtures cover actual native array import, source distance,
  # constructor, exclusions and modulo-four phase across all256 epochs.
  scan=host(base)
  def scanhost():
   for slot in range(6):scan.m[H.W.address(base,'Enemy_Flag')+slot]=0
   scan.s[0x61c]=scan.s[0x6e0]=scan.s[0x6de]=0
   return scan
  for phase in range(256):
   h=scanhost();h.s[0xa6]=phase;enemy(h,0);Q.call(h,'PpNativeProxyIn')
   assert bool(h.s[0x6e0])==(phase&3==2),(phase,h.s[0x6e0]);counts['phase_admission']+=1
  for slot,x,dx,face,ID in itertools.product(range(6),[0,239,255,256,511,1023],[-104,-103,-32,0,32,103,104],[1,2],[0,6]):
   if not 0<=x+dx<=65535:continue
   h=scanhost();N.put(h.m,Player_X_Position=x&255,Player_PageLoc=x>>8);h.s[0xa6]=2;enemy(h,slot,x=x+dx,ID=ID,Enemy_MovingDir=face)
   before=bytes(h.m[:256])+bytes(h.m[512:2048]);maps=h.m.rawtags[:];smc=bytes(h.m[0x15a:0x17b]);c,low=Q.call(h,'PpNativeProxyIn');cost.append(c.processorCycles);minimum=min(minimum,low)
   admitted=abs(dx)<104;assert bool(h.s[0x6e0])==admitted,(slot,x,dx)
   if admitted:
    assert h.s[0x61c]==128|slot and h.s[0x6d0]==1 and h.s[0x6de]==0
    assert int.from_bytes(h.s[0x61d:0x61f],'little')==x+dx+8
    assert int.from_bytes(h.s[0x61f:0x621],'little')==128
    assert h.s[0x623]==(255 if face==1 else 0)
    assert(h.s[0x624],h.s[0x625],h.s[0x626])==(57,171,1)
    assert bytes(h.s[0x710:0x713])==bytes([slot,0,255])
   assert bytes(h.m[:256])+bytes(h.m[512:2048])==before and h.m.rawtags==maps and bytes(h.m[0x15a:0x17b])==smc
   counts['scan_geometry']+=1
  for field,values in [('Enemy_Flag',[0,2,128,255]),('Enemy_ID',[7,8,13,21,46,255]),('Enemy_State',[32,33,255]),('Enemy_BoundBoxCtrl',[0,1,2,4,255]),('Enemy_Y_HighPos',[0,2,255])]:
   for value in values:
    h=scanhost();N.put(h.m,Player_X_Position=48,Player_PageLoc=0);h.s[0xa6]=2;enemy(h,0,**{field:value});Q.call(h,'PpNativeProxyIn');assert not h.s[0x6e0];counts['excluded_native_actors']+=1
  # Closest of six; ties preserve the source scan's descending slot order.
  for xs,want in [([90,89,88,87,86,85],5),([80]*6,5),([80,90,100,110,120,130],0)]:
   h=host(base);h.s[0xa6]=2
   for slot,x in enumerate(xs):enemy(h,slot,x=x)
   Q.call(h,'PpNativeProxyIn');assert h.s[0x61c]==128|want;counts['closest']+=1
  episodes=[]
  for sword in [0,1,2]:
   h=host(base);h.s[0x6ee]=sword;enemy(h,0,x=80);rows=[];start=events['actual_native_defeat']
   for frame in range(360):
    N.put(h.m,FrameCounter=frame&255,SavedJoypad1Bits=128 if frame>=40 else 0)
    Q.call(h,'PpNativeProxyIn');h.source('PpNativeTick')
    r0=H.W.address(base,'R0');scratch=bytes(h.m[r0:r0+8]);smc=bytes(h.m[0x15a:0x17b]);maps=h.m.rawtags[:]
    c,low=Q.call(h,'PpNativeProxyOut');minimum=min(minimum,low)
    assert bytes(h.m[r0:r0+8])==scratch and bytes(h.m[0x15a:0x17b])==smc and h.m.rawtags==maps
    if frame%4==0:rows.append(dict(Main=frame,action=h.s[0x616],pose=h.s[0x617],sword=h.s[0x6ee],HP=h.s[0x6cf],guardHP=h.s[0x6d0],guardDead=h.s[0x6de],nativeState=native(h,'Enemy_State'),Y=h.s[0x611],guardY=h.s[0x61f],input=h.s[0x40a],source401=h.s[0x401],face=h.s[0x615],guardFace=h.s[0x623],visible=h.s[0x6e0]))
    if native(h,'Enemy_State')&32:break
   if sword:
    if not(native(h,'Enemy_State')&32 and events['actual_native_defeat']-start==1):
     (O/'native-proxy-negative-v41.json').write_text(json.dumps(dict(qualified=False,sword_fixture=sword,trace=rows),indent=2)+'\n')
     raise AssertionError(('Armed strike failed',sword,rows[:14],rows[-2:]))
   else:assert events['actual_native_defeat']==start and h.s[0x6ee]==0
   assert N.get(h.m,'NumberofLives')==2
   episodes.append(dict(explicit_CPU_fixture_sword=sword,Main_updates=frame+1,genuine_native_defeats=events['actual_native_defeat']-start,trace=rows))
  # Source incoming entry includes the actual defender-parry gate ACEC.
  for action,expectHP in [(0,4),(62,5),(69,5),(74,5)]:
   h=host(base);h.s[0x6ee]=2;h.s[0x616]=action;h.s[0x617]=171;Q.call(h,'PpBattle_4_ACEC',args=(0,0,0,0x21));assert h.s[0x6cf]==expectHP,(action,h.s[0x6cf]);counts['incoming_gate']+=1
  h=host(base);h.s[0x6ee]=2;Q.call(h,'PpBattle_4_ACEC',args=(0,0,0,0x21));rows=[]
  assert(h.s[0x6cf],h.s[0x616])==(4,74)
  for frame in range(100):
   N.put(h.m,FrameCounter=frame&255,SavedJoypad1Bits=0);h.source('PpNativeTick')
   if frame%4==0:rows.append(dict(Main=frame,action=h.s[0x616],pose=h.s[0x617],HP=h.s[0x6cf]))
   if h.s[0x616]==0:break
  assert h.s[0x616]==0 and h.s[0x6cf]==4,('Full hurt recovery failed',rows)
 finally:N.NesMPU=original
 result=dict(passed=True,in_memory_CPU_only=True,native_emulator=False,ROM_written=False,hardware_placement_qualified=False,base_SHA256=M.A.PIN,CPU_cases=dict(counts),CPU_range=[min(cost),max(cost)],minimum_SP=minimum,actual_native_events=dict(events),original_battle_episodes=episodes,armed_hurt_recovery=rows,native_R0_R7_SMC_mapper_preserved=True,scope='Explicit CPU actor/sword fixtures execute the actual613b host and genuine ShellOrBlockDefeat after original guardHP/death predicates. No native enemy result is seeded. Synthetic4000/4400 component addresses are not a hardware placement proof; final relink/cold/runtime/ISR and native gameplay remain required.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-proxy-v40.bin',O/'native-battle-v40.bin',O/'combat-tail-CPU-v36.json',M.A.BASE]})
 (O/'native-proxy-CPU-v41.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','original_battle_episodes','armed_hurt_recovery']}))


if __name__=='__main__':main()
