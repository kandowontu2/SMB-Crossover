"""Finite Chip/Dale real Main components, with no acquired HP/box/life seeds."""
from pathlib import Path
import hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_rygar_powerups_prepare_v1 import ALLOWED,setup as base_scene
R=Path(__file__).resolve().parents[2];B=R/'build';SHA='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PLAN=[dict(name='native-entrance-crate-pickup',kind='entrance',limit=70,image=True),
 dict(name='hide-behind-real-crate',kind='hide',limit=120,image=True),
 dict(name='real-contact-before-mushroom',kind='hurt',limit=160),
 dict(name='mushroom-replenishes-one-HP',kind='food',pickup=0,limit=80,image=True),
 dict(name='lift-authored-brick',kind='lift',limit=70,image=True),
 dict(name='physical1Up-keeps-HP-food-held',kind='life',limit=120,image=True),
 dict(name='retained-horizontal-throw-contact',kind='throw',up=False,limit=180,image=True),
 dict(name='first-contact-before-flower',kind='hurt',limit=160),
 dict(name='second-contact-before-flower',kind='hurt',limit=160,image=True),
 dict(name='flower-restores-real-two-HP-deficit',kind='food',pickup=1,limit=80,image=True),
 dict(name='lift-second-authored-brick',kind='lift',limit=70),
 dict(name='upward-throw-contact',kind='throw',up=True,limit=180,image=True)]
# Eight screenshots: omit the initial carry (entrance) and use the later lift.
PLAN[0]['image']=False
FORBIDDEN='CdHealth CdFlowers CdStars CdMagic CdReady CdHeld CdHide CdThrowAge CdThrowUp CdHurtTimer CdBoxKind CdBoxMode CdBoxX CdBoxY CdBoxVX CdBoxVYLo CdBoxVYHi CdBoxAge CdEntrancePending NumberofLives PlayerStatus PlayerSize InjuryTimer GuestPowerupActive GuestHurtTicks MmDeathFlag CheatInvincible FloateyNum_Control FloateyNum_Timer'.split()
def boxes(q):return[(i,q.get('CdBoxKind',i),q.get('CdBoxMode',i))for i in range(6)if q.get('CdBoxKind',i)]
def snapshot(q):return{n:q.get(n)for n in['CdHealth','CdHeld','CdHide','CdThrowAge','CdFlowers','CdStars','PlayerStatus','NumberofLives']}
def enemy(q,x,y):
 for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,Enemy_BoundBoxCtrl=9,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0).items():q.set(n,v,0)
def scene(q,task):
 assert not any(k and mode==2 for _,k,mode in boxes(q))and q.get('CdThrowAge')==0
 base_scene(q,dict(kind='idle',face=1,hit=False))
 if task['kind']=='entrance':
  resting=[i for i,k,m in boxes(q)if m==0];assert len(resting)==1
  i=resting[0];x=q.get('CdBoxX',i)-16;assert q.get('CdBoxPage',i)==0 and 24<=x<=208
  q.put(Player_X_Position=x,MmOldX=x)
 elif task['kind']=='food'or task['kind']=='life':
  p=task.get('pickup',3)
  for n,v in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_BoundBoxCtrl=3,Enemy_X_Position=112,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_SprAttrib=0,PowerUpType=p,InvPickupOwner=255,InvPickup=252).items():q.set(n,v,5)
 elif task['kind']=='lift':q.set('Block_Buffer_1',0x51,10*16+8)
 elif task['kind']=='hurt':enemy(q,116,184)
def campaign(b,variant,mode):
 q=Arena(b,14);q.put(CdVariant=variant,CrossoverBehaviorVersion=mode,PlayerStatus=0,OperMode_Task=3,AreaType=1,NumberofLives=2);q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit')
 names=['GameLoop','CdEnsureInit','CdSpawnEntrance','CdPickResting','CdLiftBrick','CdRelease','CdBodyContact','CdDefeatEnemy','CdInjury','CdCollectPickup','HandlePowerUpCollision','FloateyNumbersCore']
 owners={(address(b,n),(location(b,n)-16)//8192):n for n in names};original=NesMPU.step;task={'kind':'cold','name':'cold'};rec={};age=0;calls=0;records=[];health_writers={}
 def step(c):
  k=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;n=owners.get((c.pc,k))
  if n:
   if n not in rec['owners']:rec['owners'].append(n)
   if n=='HandlePowerUpCollision':assert c.x==5;rec['collisions']+=1
   if n=='CdCollectPickup'and task['kind']=='food':assert c.x==5;rec['food_entries']+=1
   if n=='CdDefeatEnemy':assert c.x==0;rec['defeats']+=1
   if n=='CdInjury':rec['injury_entries']+=1
   if n=='CdRelease'and q.get('CdHeld'):rec['releases']+=1
  original(c)
 def blank():return dict(owners=[],collisions=0,food_entries=0,defeats=0,injury_entries=0,releases=0,health_writes=[])
 def tick(bits=0):
  nonlocal calls
  q.set('SavedJoypadBits',bits);_,writes=q.invoke('GameLoop');calls+=1
  assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8 and q.get('GuestPowerupActive')==0
  for w in writes:
   if w['address']==address(b,'CdHealth'):
    rec['health_writes'].append(dict(age=age,**w))
    if task['kind']in['food','hurt']:
     kind='injury'if task['kind']=='hurt'else'small-food'if task['pickup']==0 else'full-food';at=16+w['bank']*8192+(w['pc']&8191);o=dict(pc=w['pc'],bank=w['bank'],bytes=list(b['raw'][at:at+3]),kind=kind)
     if(w['pc'],w['bank'])in health_writers:assert health_writers[(w['pc'],w['bank'])]==o
     health_writers[(w['pc'],w['bank'])]=o
  ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
  return writes
 rec=blank();NesMPU.step=step
 try:
  scene(q,task)
  for age in range(30):tick()
  assert q.get('CdHealth')==3 and q.get('CdMagic')==165 and q.get('CdReady')==67 and len(boxes(q))==1 and q.get('CdHeld')==0
  cold=snapshot(q)
  for task in PLAN:
   scene(q,task);rec=blank()|dict(name=task['name'],kind=task['kind'],before=snapshot(q));records.append(rec);placed=False;hurt=False
   if task['kind']in['lift','entrance']:assert q.get('CdHeld')==0
   if task['kind']in['hide','life','throw']:assert q.get('CdHeld')>0
   if task['kind']=='life':assert q.get('PlayerStatus')==1 and q.get('CdHealth')==3
   for age in range(task['limit']):
    if task['kind']=='hide'and age>=12 and not placed:enemy(q,116,184);placed=True
    if task['kind']=='throw'and not placed:
     live=[i for i,k,m in boxes(q)if m==2]
     if live:
      i=live[0];rec.setdefault('first_throw',age);x,y=q.get('CdBoxX',i),q.get('CdBoxY',i)
      if age>=rec['first_throw']+4 and q.get('CdBoxPage',i)==0 and 136<=x<=220 if not task['up']else age>=rec['first_throw']+4 and 56<=y<=160:
       enemy(q,x+6,y-8);placed=True
    bits=64 if task['kind']in['entrance','lift','throw']and 5<=age<=8 else 0
    if task['kind']=='throw'and task['up']and bits:bits|=8
    if task['kind']=='hide'and not rec['defeats']:bits=4
    tick(bits)
    assert q.get('CdFlowers')==q.get('CdStars')==0,'Unused counters are not invented upgrades'
    if task['kind']=='hurt':
     if q.get('CdHealth')<rec['before']['CdHealth']:
      assert q.get('CdHealth')==rec['before']['CdHealth']-1 and rec['injury_entries']>0
      if not hurt:q.set('Enemy_Flag',0,0);hurt=True
      if q.get('CdHurtTimer')==q.get('InjuryTimer')==0:break
    elif task['kind']=='food':
     if age>=24:
      assert rec['collisions']==rec['food_entries']==1 and q.get('Enemy_Flag',5)==0,(task,rec,snapshot(q),q.get('Enemy_Flag',5))
      assert q.get('CdHealth')==(min(3,rec['before']['CdHealth']+1)if task['pickup']==0 else 3)and q.get('PlayerStatus')==task['pickup']^1
      break
    elif task['kind']in['entrance','lift']:
     if age>=16:
      assert q.get('CdHeld')and q.get('CdBoxMode',q.get('CdHeld')-1)==1
      if task['kind']=='lift':assert q.get('Block_Buffer_1',10*16+8)==0
      break
    elif task['kind']=='hide':
     if age>=40 and rec['defeats']:
      assert placed and q.get('CdHealth')==rec['before']['CdHealth']and q.get('CdHeld')==0 and boxes(q)==[];break
    elif task['kind']=='life':
     assert q.get('CdHealth')==rec['before']['CdHealth']and q.get('PlayerStatus')==rec['before']['PlayerStatus']and q.get('CdHeld')==rec['before']['CdHeld']
     if q.get('NumberofLives')==rec['before']['NumberofLives']+1 and q.get('FloateyNum_Control',5)==0:
      assert rec['collisions']==1;break
    elif task['kind']=='throw'and age>=150:
     assert placed and rec['defeats']==rec['releases']==1 and q.get('CdHeld')==0 and boxes(q)==[];break
    if task['kind']!='hurt':assert q.get('CdHurtTimer')==q.get('InjuryTimer')==0,(task,age,'Unexpected contact')
   else:raise AssertionError(('Finite source stage incomplete',variant,mode,task,rec,snapshot(q),boxes(q)))
   rec.update(updates=age+1,after=snapshot(q));assert q.get('CdHealth')>0
 finally:NesMPU.step=original
 return dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=SHA,variant=variant,mode=mode,cold=cold,GameLoop_calls=calls,plan=PLAN,cases=records,health_writers=list(health_writers.values()),source_context='Standalone cold PlayerStatus0/lives2/timer399 context is explicitly staged. No subsequent acquired health, food status, held object, life, ammo, immunity or outcomes seeded. Real source cold initialization creates3HP and entrancecrate. Logical actor/map/position staging and real PPU queue consumer between Main calls are disclosed; no native timing/image proof.',limits='Hard native planned for both identities. Easy source only; Star2/random drop/full natural emergence, general climbing/death/life rollover/foreign family, waveform and blanket art remain open.')
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();rom=B/'cv3_life_gain_watch.nes';assert sha(rom)==SHA and not a.output.exists();b=scoped_load(rom)
 result=dict(passed=True,native_run=False,campaigns=[campaign(b,v,m)for v,m in itertools.product([0,1],[0,1])]);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,output=str(a.output),sha256=sha(a.output),calls=sum(c['GameLoop_calls']for c in result['campaigns']))))
