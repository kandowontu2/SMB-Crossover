"""Run proposed Tank host callbacks against actual frozen native owners."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import P,O,PIN,REF
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 assembly=json.loads((O/'host-assembly.json').read_text());assert assembly['passed']and sha(REF.read_bytes())==assembly['source_bindings'][str(REF.relative_to(R))]
 labels={q[2][1:]:int(q[1],16)for line in(O/'host.lbl').read_text().splitlines()if len(q:=line.split())==3}
 code=(O/'host.bin').read_bytes();measured={}
 def fresh(**values):
  m=M.fresh(b);m.ram[2][0x1600:0x1600+len(code)]=code
  M.put(m,SelectedCharacter=0,MarioVariant=7,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,PlayerStatus=1,PlayerSize=0,Player_State=0,Player_CollisionBits=3,Player_Y_Position=160,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=0,PlayerFacingDir=1,Player_MovingDir=1,AreaType=1,ObjectOffset=0,NmiDisable=255)
  M.put(m,**values);return m
 def call(m,name,*,a=85,x=0,y=91,p=0x31):
  if name not in labels:return M.invoke(m,name,a=a,x=x,y=y,p=p)
  target=labels[name];m[address(b,'SafecallA_SMC')+1]=a;m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
  c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=2;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff);low=c.sp
  for _ in range(200000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags);c.step();low=min(low,c.sp)
  else:raise AssertionError((name,'bounded'))
  assert c.sp==224 and m.rawtags[1]==M.get(m,'CurrentBank')and m.rawtags[2]==M.get(m,'CurrentBankC')
  q=measured.setdefault(name,dict(calls=0,max_cycles=0,minimum_SP=224));q['calls']+=1;q['max_cycles']=max(q['max_cycles'],c.processorCycles);q['minimum_SP']=min(q['minimum_SP'],low)
  return dict(A=c.a,X=c.x,Y=c.y,P=c.p,minimum_SP=low)
 def state(m,c):
  omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))
  # Native farcall bookkeeping target reflects the wrapper's final callback.
  omit.update(range(0x15a,0x17b));omit.update([address(b,'CurrentBank'),address(b,'CurrentBankC'),address(b,'safecall_a')])
  return tuple(c[n]for n in['A','X','Y','P']),bytes(v for i,v in enumerate(m[:0x8000])if i not in omit),[bytes(q)for q in m.ram]
 # Foreign Mario variants go through exactly the original owner, including
 # Flash Mario0/Maaa2, Kamikaze3, Celeste4 and native Toad5/Peach6.
 foreign=0
 for variant,pair,flags in itertools.product(range(7),[('MtHostContact','S2BoundaryImmunity'),('MtHostMovement','BmMarioMovement'),('MtHostGrowthUpdate','MarioSourcePowerupUpdate'),('MtHostBeginPowerup','MarioSourceBeginPowerup'),('MtHostInjury','CmHostMarioInjury')],[0x30,0x71]):
  seed=fresh(MarioVariant=variant,PowerUpType=0);left=M.fork(seed);right=M.fork(seed)
  x=call(left,pair[0],p=flags);y=call(right,pair[1],p=flags)
  assert state(left,x)==state(right,y),('Foreign owner difference',variant,pair,state(left,x)[0],state(right,y)[0]);foreign+=1
 contact=0
 for enemy,slot,area in itertools.product([0,1,2,3,4,6,13],range(6),[0,1]):
  m=fresh(PlayerStatus=2,AreaType=area,ObjectOffset=slot)
  for field,value in dict(Enemy_ID=enemy,Enemy_Flag=1,Enemy_State=0,Enemy_Y_Position=160,Enemy_Y_HighPos=1,Enemy_X_Position=112,Enemy_PageLoc=0,Enemy_MovingDir=1).items():m[address(b,field)+slot]=value
  c=call(m,'MtHostContact',x=slot,y=enemy)
  assert c['P']&1 and m[address(b,'Enemy_State')+slot]&32
  assert m[address(b,'FloateyNum_Control')+slot]==6 and M.get(m,'Square1SoundQueue')==8
  if enemy==13:assert m[address(b,'Enemy_Flag')+slot]==0 and m[address(b,'Enemy_Y_HighPos')+slot]==2
  contact+=1
 inactive=0
 for status,star in itertools.product([0,1],[0,32]):
  m=fresh(PlayerStatus=status,StarInvincibleTimer=star,Enemy_ID=7,Player_Y_Position=176)
  # Unlike the Flash Mario baseline, source Tank must not swallow the
  # standing-blooper contact before the ordinary native star/injury branch.
  c=call(m,'MtHostContact');assert not c['P']&1;inactive+=1
 injury=0
 for status,flags in itertools.product([1,2],[0x30,0x31,0x71,0xf1]):
  m=fresh(PlayerStatus=status);before=[bytes(z)for z in m.ram]
  c=call(m,'MtHostInjury',p=flags)
  if status==2:assert M.get(m,'PlayerStatus')==2 and M.get(m,'GameEngineSubroutine')==8 and M.get(m,'TimerControl')==0 and [bytes(z)for z in m.ram]==before
  else:assert M.get(m,'PlayerStatus')==0 and M.get(m,'GameEngineSubroutine')==10 and M.get(m,'TimerControl')==255 and M.get(m,'InjuryTimer')==8 and M.get(m,'Square1SoundQueue')==16
  injury+=1
 pickup=0
 for status,kind,behavior in itertools.product(range(3),[0,1],[0,1]):
  m=fresh(PlayerStatus=status,PlayerSize=int(status==0),PowerUpType=kind,CrossoverBehaviorVersion=behavior)
  call(m,'MtHostBeginPowerup')
  assert M.get(m,'PlayerStatus')==min(status+1,2)
  assert M.get(m,'GameEngineSubroutine')==(9 if status==0 else 8)
  assert M.get(m,'TimerControl')==(255 if status==0 else 0)
  pickup+=1
 growth=0
 for timer,size in itertools.product([0,195,196,197,247,248,249,255],[0,1]):
  m=fresh(TimerControl=timer,GameEngineSubroutine=9,PlayerSize=size,PlayerChangeSizeFlag=0)
  call(m,'MtHostGrowthUpdate')
  assert M.get(m,'PlayerSize')==(size^1 if timer==248 else size)
  assert M.get(m,'GameEngineSubroutine')==(8 if timer==196 else 9)
  assert M.get(m,'TimerControl')==(0 if timer==196 else timer);growth+=1
 movement=0
 fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed','Player_State','Player_X_Scroll','Player_X_MoveForce','Player_Y_MoveForce','CrouchingFlag','VerticalForce','MaximumLeftSpeed','MaximumRightSpeed']
 for state_,swim,lr,ab in itertools.product(range(4),range(2),range(4),[0,64,128,192]):
  seed=fresh(Player_State=state_,SwimmingFlag=swim,Left_Right_Buttons=lr,A_B_Buttons=ab,Up_Down_Buttons=4 if lr==3 else 0,PreviousA_B_Buttons=0,Player_X_Speed=24,Player_XSpeedAbsolute=24)
  left=M.fork(seed);right=M.fork(seed);call(left,'MtHostMovement');call(right,'CrossoverVanillaMovement')
  assert[M.get(left,n)for n in fields]==[M.get(right,n)for n in fields],('Native movement mismatch',state_,swim,lr,ab);movement+=1
 q=dict(passed=True,base_ROM_sha256=PIN,component_bytes=len(code),host_callback_bytes=labels['MtHostEnd']-labels['MtHostSelected'],preloaded_RAM2_fixture=True,actual_A2_farcall_transport=True,owning_link=False,native_emulator=False,installed=False,foreign_owner_differential_cases=foreign,authentic_contact_cases=contact,Tank_inactive_native_blooper_cases=inactive,injury_cases=injury,pickup_cases=pickup,native_growth_milestone_cases=growth,native_SMB_movement_cases=movement,measured=measured,
  scope='Source-assembled host callbacks invoke actual native stun/score/palette/growth/injury/SMB movement owners in frozen e401 host, through real FarCallCommon rawbank2 at aliasB600. PhysicalRAM2offset1600 code is explicitly preloaded, not a lease or installed loader. Exact source call substitutions are proposed only; global identity/header admission, outer Main/ISR/visual/full-stage qualification remains.',
  assumptions=['Current1c and proposed HUD successor change Karnov owners only; actual final owning-link checks must bind Tank callback imports and confirm these native Mario paths remain unchanged.','Terrain now has a separate real-native CPU receipt; final transport/loader, boots pickup/boot-only art, menu/lives/selection publication and PRG/CHR/RAM/OAM funding remain independent integration gates.'],bindings={str(REF.relative_to(R)):sha(REF.read_bytes()),str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes()),'host.bin':sha(code)})
 (O/'host-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k.endswith('cases')or k in['passed','component_bytes','measured']}))

if __name__=='__main__':main()
