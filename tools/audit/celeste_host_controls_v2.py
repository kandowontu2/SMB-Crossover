"""Actual assembled Celeste host controls; typed source arenas, no native claim."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import seed,run,registers,app,cleanwrites,scoped_load,sha,address,location,NesMPU,smc_at

def cmseed(b,tier=0):
 q=seed(b,0);q.put(MarioVariant=4,CmMarker=0,CmActive=0,Player_X_Position=96,Player_Y_Position=160,PlayerFacingDir=1,ScreenRight_PageLoc=1,ScreenRight_X_Pos=255)
 run(q,'MenuResolveCharacter');q.put(CmTier=tier,PlayerStatus=tier);return q

def execute(q,name,observe=(),**kw):
 b=q.b;s=b['syms'][name];g=b['segs'][s['seg']];pc=address(b,name);win=(pc-0x8000)//8192;bank=(int(g['ooffs'],0)-16)//8192;q.m.page(win,bank)
 if win in[1,2]:q.set('CurrentBank' if win==1 else 'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.a=kw.get('a',0);c.x=kw.get('x',0);c.y=kw.get('y',0);c.p=kw.get('p',0x30);c.stPushWord(0x5aff)
 hits={n:[] for n in observe}
 for _ in range(300000):
  if c.pc==0x5b00:assert c.sp==253;return c,hits
  for n in hits:
   if c.pc==address(b,n):
    sg=b['segs'][b['syms'][n]['seg']];physical=(int(sg['ooffs'],0)-16)//8192
    if q.m.banks[(c.pc-0x8000)//8192]==physical:hits[n].append((c.processorCycles,c.x,c.y,q.get('Player_Y_Speed')))
  c.step()
 raise AssertionError((name,'timeout',hex(c.pc)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 b=scoped_load(a.rom);old=scoped_load(a.baseline);proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={},bindings={str(z):sha(z) for z in[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.baseline,a.baseline.with_suffix('.dbg'),R/'tools/audit/sunny_integrated_controls_v1.py']});ck=proof['checks']
 try:
  rows=[]
  for char,var,obj,flags in itertools.product(range(24),[0,1],[0,233],[0x30,0x31,0x70,0x71]):
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.put(MarioVariant=var,ObjectMetasprite=obj,CmActive=0) if 'CmActive' in bundle['syms'] else q.put(MarioVariant=var,ObjectMetasprite=obj)
    c,w,_=run(q,'CrossoverGraphicsBank',a=87,x=177,y=9,p=flags);pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
   assert pair[0][:4]==pair[1][:4],('resident',char,var,obj,flags,pair[0][0],pair[1][0]);rows.append(pair[1][4]-pair[0][4])
  ck['resident_foreign']=dict(passed=True,cases=len(rows),CPU_delta=[min(rows),max(rows)])
  for var,expected in[(0,8),(1,0),(4,1),(0,8)]:
   # Actual Select -> resolver sequence, not a direct SelectedCharacter write.
   q=seed(b,0);q.put(CrossoverMenuIndex=0,MarioVariant=var,CrossoverMenuPressed=32);run(q,'NrMenuToggle');want={0:1,1:4,4:0}[var];assert q.get('MarioVariant')==want
   run(q,'MenuResolveCharacter');assert q.get('SelectedCharacter')==(8 if want==1 else 0) and q.get('CmActive')==int(want==4)
  ck['menu']=dict(passed=True,cycle=[0,1,4,0],unimplemented_2_3_skipped=True)
  q=cmseed(b,2);q.put(AreaPointer=194);before=bytes(q.m[0x5c00:0x5c80]);run(q,'CmHostEnsure');assert q.get('CmTier')==2 and bytes(q.m[0x5c00:0x5c80])==before
  q.set('AreaAddrsLOffset',6);run(q,'NrReset');assert q.get('CmArea')==0x26 and q.get('CmTier')==2
  q.set('NumberofLives',3);run(q,'NrReset');assert q.get('CmTier')==2
  q.set('NumberofLives',2);run(q,'NrReset');assert q.get('CmTier')==0
  q.put(CmTier=2);run(q,'NrFreshGameInit');assert q.get('CmTier')==0 and q.get('CmActive')==1
  q.put(CrossoverMenuIndex=1);run(q,'MenuResolveCharacter');assert q.get('CmActive')==0
  ck['lifecycle']=dict(passed=True,future_pipe_and_area=True,real_life_loss_and_gain=True,fresh_game=True,inactive_overlay_not_cleared=True)
  n=0
  for mode,tier,face,buttons in itertools.product([0,1],range(3),[1,2],[0,1,129,64,65,4]):
   q=cmseed(b,tier);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,SavedJoypadBits=buttons,A_B_Buttons=buttons&192,Left_Right_Buttons=buttons&3,Up_Down_Buttons=buttons&12,Player_State=0,GameTimerDisplay=4,PlayerEntranceCtrl=2)
   for step in range(2):
    q.put(VRAM_Buffer1_Offset=0,VRAM_Buffer2_Offset=0)
    c,h=execute(q,'GameLoop',observe=['CmMovement','MarioSourceMovement','CrossoverVanillaMovement','CmAfterBG','CmWeapons','CmDraw','ProcFireball_Bubble::ProcAirBubbles','BubbleCheck'])
    assert len(h['CmMovement'])==1 and not h['MarioSourceMovement'] and not h['CrossoverVanillaMovement'],('integrator',mode,tier,face,buttons,h)
    assert len(h['CmAfterBG'])==1 and len(h['CmWeapons'])==1 and len(h['CmDraw'])==1 and len(h['ProcFireball_Bubble::ProcAirBubbles'])==1,h
    assert q.get('PlayerSize')==0 and q.get('PlayerStatus')==q.get('CmTier') and q.get('NmiDisable')==0
    assert q.m.banks[2]==98 and q.get('CurrentBankC')==226 and q.get('ObjectMetasprite') in[0,233]
    assert [q.get('X5ChrMode',j) for j in range(4)]==[130]*4
    n+=1
  ck['actual_GameLoop']=dict(passed=True,calls=n,both_modes=True,typed_empty_map=True,one_integrator_BG_dash_and_bubble_tail=True,C98_publication=True)
  n=0
  for mode,tier,slot,kind in itertools.product([0,1],range(3),range(6),range(4)):
   q=cmseed(b,tier);q.put(CrossoverBehaviorVersion=mode,ObjectOffset=(slot+1)%6);q.set('PowerUpType',kind,slot);q.set('Enemy_Flag',1,slot);q.set('Enemy_State',0x80,slot);q.set('Enemy_ID',0x2e,slot)
   c,_,_=run(q,'NrPickupCollision',x=slot);assert c.p&1
   run(q,'NrPickup',x=slot)
   if kind<2:assert q.get('CmTier')==min(2,tier+1) and q.get('FloateyNum_Control',slot)==6 and q.get('Enemy_Flag',slot)==0
   elif kind==2:assert q.get('StarInvincibleTimer')==0x23 and q.get('CmTier')==tier
   else:assert q.get('FloateyNum_Control',slot)==11 and q.get('CmTier')==tier
   n+=1
  ck['actual_pickups']=dict(passed=True,cases=n,actual_X_and_stale_ObjectOffset=True,native_star_life_fallback=True)
  n=0
  for tier,flags in itertools.product([1,2],range(0x30,0x40)):
   q=cmseed(b,tier);q.put(ObjectOffset=1);run(q,'ForceInjury',p=flags)
   assert q.get('CmTier')==tier-1 and q.get('PlayerStatus')==tier-1 and q.get('InjuryTimer')==0x90 and q.get('GameEngineSubroutine')==8
   n+=1
  ck['ForceInjury']=dict(passed=True,cases=n,real_native_caller=True)
  costs={}
  for name in['NrUi','NrStatusName','NrColors','NrPrivate','NrRise','NrPickupCollision','NrInjuryStatus','GameLoop']:
   ds=[]
   for char in[0,1,2,3,4,5,8,9,15,20,21,23]:
    pair=[]
    for bundle in[old,b]:
     q=seed(bundle,char);q.put(MarioVariant=0,TimerControl=1,InvHudActive=0);q.set('PowerUpType',2,2)
     if 'CmActive' in bundle['syms']:q.set('CmActive',0)
     c,w,_=run(q,name,a=1,x=2,y=93,p=0x71);pair.append((registers(c),app(q),cleanwrites(q,w),q.m.banks,c.processorCycles))
    assert pair[0][:4]==pair[1][:4],('foreign',name,char,pair[0][0],pair[1][0]);ds.append(pair[1][4]-pair[0][4])
   costs[name]=[min(ds),max(ds)]
  ck['foreign']=dict(passed=True,cases=len(costs)*12,CPU_delta=costs,actual_complete_GameLoop=True,leaf_negative_retained='build/celeste_host_controls_v1.json',leaf_limit='Native JumpEngine table/target scratch R4/R6/R7 holds genuine moved code addresses at PlayerMovementSubs return. The complete real GameLoop overwrites these before the first downstream live boundary and is compared without RAM exclusions beyond inherited dead stack and SMC classification.')
  head=[]
  for face,tier,yp,tile in itertools.product([1,2],range(3),[160,164,168,172],[0,196,81,192]):
   q=cmseed(b,tier);q.put(PlayerFacingDir=face,Player_Y_Position=yp,Player_Y_Speed=253,Player_State=1,SmTempY=253,SmCeilingHit=0)
   run(q,'BlockBufferColli_Head',y=0);ptr=q.get('R6')+256*q.get('R7')+q.get('R2');q.m[ptr]=tile
   run(q,'PlayerBGCollision');old=q.get('Player_Y_Speed');saved=q.get('SmTempY');run(q,'RyuSourceBodyAfterBGBridge');assert saved==253
   assert q.get('SmCeilingHit')==int(old==1),(face,tier,yp,tile,old,q.get('SmCeilingHit'))
   if old==1:assert q.get('CmVelYFrac')==64
   head.append([face,tier,yp,tile,old,q.get('SmCeilingHit')])
  ck['real_head_BG_to_AfterBG']=dict(passed=True,cases=len(head),rows=head,scope='Native complete PlayerBGCollision then actual RyuSourceBodyAfterBGBridge; pre-BG signed velocity scratch is owned only by active Celeste and remains unchanged through raw0 terrain.')
  n=0
  for entry,vy in [('MegaManBounceVelocity',252),('MegaManSpringVelocity',249)]:
   for flags in [0x30,0x31,0x70,0x71]:
    q=cmseed(b,2);q.put(JumpspringForce=249);c,_,_=run(q,entry,a=87,x=33,y=17,p=flags)
    assert registers(c)==[87,33,17,flags,253] and q.get('Player_Y_Speed')==vy and q.get('Player_State')==1,(entry,registers(c))
    assert q.get('CmVelYFrac')==(96 if vy==252 else 0);n+=1
  ck['native_bounce_spring_callers']=dict(passed=True,cases=n,full_AXYP_SP=True,actual_signed_JumpspringForce=True)
  n=0
  for entry in ['CmHostMovement','CmHostGraphics','CmHostUi','NrPickupCollision','CrossoverGraphicsBank']:
   q=cmseed(b,2);q.put(PowerUpType=0,SavedJoypadBits=129,A_B_Buttons=128,Left_Right_Buttons=1)
   c,w,count=run(q,entry,p=0x30,irq=True);n+=count
  ck['real_IRQ_host_boundaries']=dict(passed=True,injections=n,scope='Every distinct enabled PC in inherited run() physical81/94/124/126/127; separate kernel98 controls are added by the seam supplement, not silently covered here.')
  proof['passed']=True
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':True,'checks':list(ck),'proof_sha256':sha(a.output)}))
if __name__=='__main__':main()
