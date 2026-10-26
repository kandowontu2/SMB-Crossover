"""Preseeded actors, real full GameCore/controller components; source feasibility only."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,location
from cv3_remaining_sfx_queue256_support_v1 import init
from cv3_remaining_sfx_steady_cpu_v4 import invoke
from cv3_dmc_complete_cpu_v1 import apu
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def traced(q,name,events):
 pc=address(q.b,name);bank=(location(q.b,name)-16)//8192;window=(pc-0x8000)//8192;q.m.page(window,bank)
 if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 hooks={address(q.b,n):(n,(location(q.b,n)-16)//8192)for n in['Cv3FxProducerFast','Cv3FxBatEnter','Cv3DmcPrimaryQueue','Cv3DmcFullInjuryQueue','Cv3InjuryStartGate','KillPlayer','Cv3CollectPickupGate']};q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.stPushWord(0x5aff)
 for _ in range(150000):
  if c.pc==0x5b00:assert c.sp==253;return c
  if c.pc in hooks:
   n,b=hooks[c.pc]
   if q.m.banks[(c.pc-0x8000)//8192]==b:events.append(dict(owner=n,A=c.a,X=c.x,pending=q.get('Cv3DmcPending'),health=q.get('Cv3Health',q.get('Cv3Variant')-1),owned=q.get('Cv3FxOwned')))
  c.step()
 raise AssertionError(('Actual GameCore timeout',hex(c.pc),q.m.banks))
def seed(b,variant,mode):
 q=init(b,variant);q.put(CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaPointer=0x25,AreaType=1,WorldNumber=0,Cv3ActiveVariant=variant,Cv3LastArea=0x25,Cv3LastWorld=0,Cv3LastLife=q.get('NumberofLives'),Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerSize=0,PlayerStatus=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,PlayerFacingDir=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollLock=1,GameEngineSubroutine=8,DisableCollisionDet=0,TimerControl=0,CurrentPlayer=0,InjuryTimer=0,Cv3Invul=0,GuestInvulTicks=0,EnemyFrenzyBuffer=0,EnemyFrenzyQueue=0,AreaParserTaskNum=0,ScrollThirtyTwo=0)
 q.set('Cv3Ready',1,variant-1);q.set('Cv3Hearts',64,variant-1);q.set('Cv3Health',64,variant-1);q.set('Cv3Power',0,variant-1);q.set('Cv3Subweapon',2,variant-1);q.array('Enemy_Flag',[0]*6);q.array('Block_State',[0]*2);q.array('Misc_State',[0]*9)
 for i in range(416):q.set('Block_Buffer_1',0,i);q.set('MmSolidTerrain',0,i)
 for page in range(2):
  for x in range(16):q.set('Block_Buffer_1',0x54,page*208+176+x);q.set('MmSolidTerrain',1,page*208+176+x)
 q.put(EnemyDataLow=address(b,'E_GroundArea10')&255,EnemyDataHigh=address(b,'E_GroundArea10')>>8);q.array('GameTimerDisplay',[3,0,0]);return q
def enemy(q,x,speed):
 for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=1,Enemy_X_Speed=speed,Enemy_Y_Speed=0,Enemy_BoundBoxCtrl=9).items():q.set(n,v)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);cases=[]
 for profile,mode in[('mixed',0),('mixed',1),('priority',1),('death',0),('death',1)]:
  q=seed(b,3 if profile=='death'else 2,mode)
  if profile=='mixed':enemy(q,4,16)
  elif profile=='death':q.set('Cv3Health',1,2);enemy(q,32,16)
  else:
   for n,v in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,PowerUpType=1,InvPickup=0xd3,InvPickupOwner=5,Cv3PickupVariant=2,InvRisePhase=0).items():q.set(n,v,5)
  history=[]
  for frame in range(100):
   bits=0
   if 4<=frame<=6:bits=0x84 if profile=='death'else 0x48
   if profile=='mixed'and 32<=frame<=34:bits=0x40
   if profile=='priority':
    if 18<=frame<=34:bits|=1
    if 36<=frame<=38:bits|=0x48
   q.put(SavedJoypadBits=bits);q.put(FrameCounter=(q.get('FrameCounter')+1)&255);events=[];traced(q,'GameCoreRoutine',events);invoke(q,'AudioUpdate');history.append(dict(frame=frame,input=bits,events=events,X=q.get('Player_X_Position'),Y=q.get('Player_Y_Position'),enemyX=q.get('Enemy_X_Position'),enemyY=q.get('Enemy_Y_Position'),health=q.get('Cv3Health',q.get('Cv3Variant')-1),sub=q.get('Cv3Subweapon',q.get('Cv3Variant')-1),gameSub=q.get('GameEngineSubroutine'),noise=q.get('Cv3FxNoiseID'),pulse=q.get('Cv3FxPulseID'),owned=q.get('Cv3FxOwned'),DMCowner=q.get('BassDmcActive'),DMCpriority=q.get('Cv3DmcPriority'),APU=apu(q)))
   if q.get('GameEngineSubroutine')!=8:break
  out=a.output/(profile+'-mode'+str(mode)+'.json');out.write_text(json.dumps(history,indent=2)+'\n');calls=[(r['frame'],e['owner'],e['A'])for r in history for e in r['events']];cases.append(dict(profile=profile,mode=mode,frames=len(history),calls=calls,history=str(out),history_sha256=sha(out)));print(json.dumps(cases[-1]),flush=True)
 r=dict(completed=True,qualification_passed=False,native_executed=False,ROM_sha256=sha(a.rom),cases=cases,scope='Exploratory source/controller/actor feasibility from preseeded RAM, actual entire assembled GameCore and audio. Only inputs/frame clock advance afterseed. No success oracle or native claim until actual event timelines reviewed. No PPU/bus/NMI timing/fullcampaign claim.',tool_sha256=sha(__file__));(a.output/'exploration.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
