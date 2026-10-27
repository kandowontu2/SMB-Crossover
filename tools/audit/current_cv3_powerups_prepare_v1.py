"""Prepare earned CV3 alternate components on explicit ab221e; never launch native."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_link_simon_powerups_prepare_v1 import setup,target,ALLOWED
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua
SHA='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
VARIANTS={'grant':1,'sypha':2,'alucard':3}
EXTRA_ALLOWED=['Cv3PickupVariant','Cv3DropType','Cv3DropX','Cv3DropPage','Cv3DropY','Cv3DropAge','Cv3DropVY','Cv3DropFrac']

def plans(v):
 def collect(item,name):return dict(kind='collect',item=item,name=name,limit=90)
 def use(name,shot=0,**kw):return dict(kind='use',item=0,name=name,shot=shot,limit=320,**kw)
 result=[collect(208,'health-capped-64'),use('primary-base',primary=True,melee=v<3,shot=6 if v==3 else 0,allocations=1 if v==3 else 0)]
 if v<3:
  for item,name,shot in [(209,'dagger'if v==1 else'flame',1 if v==1 else 3),(210,'axe'if v==1 else'ice',2 if v==1 else 4),(211,'watch'if v==1 else'orbs',0 if v==1 else 5)]:
   result +=[collect(item,'earn-'+name),use('use-'+name,shot=shot,cost=5 if v==1 and item==211 else 1,subweapon=item-208,watch=v==1 and item==211,ice=v==2 and item==210,allocations=0 if v==1 and item==211 else 3 if v==2 and item>209 else 1)]
  if v==1:result +=[dict(kind='wall',item=0,name='innate-wall-climb-leap',limit=220),dict(kind='ceiling',item=0,name='innate-ceiling-traverse-drop',limit=240)]
 else:
  for level in [1,2]:result +=[collect(212,'earn-bolt-'+str(level+1)),use('primary-bolt-'+str(level+1),primary=True,shot=6,allocations=level+1)]
  result +=[dict(kind='bat',item=0,name='native-bat-flight-restore',limit=260)]
 result +=[dict(kind='heart',item=1,name='physical-heart-one',limit=90),dict(kind='heart',item=5,name='physical-heart-five',limit=90)]
 return result

def scene(q,v,task):
 assert all(q.get('Cv3ShotType',i)==0 for i in range(4)) and q.get('Cv3AttackAge')==q.get('Cv3Climb')==q.get('Cv3Bat')==q.get('AvStopwatch')==0
 assert all(q.get('Cv3DropType',i)==0 for i in range(2)),(task['name'],[q.get('Cv3DropType',i)for i in range(2)],[q.get('Cv3DropAge',i)for i in range(2)])
 setup(q,5,dict(kind='use',item=0))
 if task['kind']=='collect':
  for n,z in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_BoundBoxCtrl=3,Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_SprAttrib=0,PowerUpType=0 if task['item']==208 else 1,InvPickupOwner=5,InvPickup=task['item'],Cv3PickupVariant=v).items():q.set(n,z,5)
 elif task['kind']=='heart':
  for n,z in dict(Cv3DropType=task['item'],Cv3DropX=72,Cv3DropPage=0,Cv3DropY=192,Cv3DropAge=0,Cv3DropVY=0,Cv3DropFrac=0).items():q.set(n,z,0)
 elif task['kind']=='wall':
  for row in range(4,12):q.set('Block_Buffer_1',0x54,row*16+7)
 elif task['kind']=='ceiling':
  for col in range(2,10):q.set('Block_Buffer_1',0x54,6*16+col)
 elif task.get('watch'):target(q,192,184);q.set('Enemy_X_Speed',248,0)

def buttons(task,age,q,t):
 if task['kind']=='use':return (64+(8 if not task.get('primary')else 0))if 6<=age<=8 else 0
 if task['kind']=='wall':return (1+8+(128 if 4<=age<=24 else 0))if age<100 else 2+128 if age<104 else 0
 if task['kind']=='ceiling':
  if 'attached_at'in t:return 2+8 if age<t['attached_at']+20 else 128 if age<t['attached_at']+24 else 0
  return 8+(128 if 4<=age<=28 else 0)
 if task['kind']=='bat':
  bat=q.get('Cv3Bat')
  if age<10:return 132 if 4<=age<=8 else 0
  if bat==1:return 0
  if bat==2:
   t.setdefault('flight_at',age)
   if age<t['flight_at']+44:return 9
   if age<t['flight_at']+62:return 1
   return 0 if q.get('Cv3Previous')&128 else 132
 return 0

def source_campaign(b,v,plan,watch_expected=90):
 q=Arena(b,5);q.put(Cv3Variant=v,PlayerStatus=0,OperMode_Task=3,AreaType=1,CrossoverBehaviorVersion=1,NumberofLives=2,AreaPointer=194,WorldNumber=0,LevelNumber=0)
 q.invoke('RosterClearState');q.invoke('InventoryInit');q.array('GameTimerDisplay',[3,9,9]);setup(q,5,dict(kind='use',item=0));q.set('SavedJoypadBits',0);q.invoke('GameLoop')
 assert q.get('Cv3Health',v-1)==64 and q.get('Cv3Hearts',v-1)==10 and q.get('Cv3Power',v-1)==q.get('Cv3Subweapon',v-1)==0
 out=[];original=NesMPU.step;t=None;age=0
 names=['GameLoop','MarioSourcePowerupCollision','Cv3CollectPickupGate','Cv3Spawn','Cv3AttackEnemies','ShellOrBlockDefeat','Cv3UpdateDrops','Cv3BatUpdate']
 owners={(address(b,n),(location(b,n)-16)//8192):n for n in names}
 def step(c):
  k=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;n=owners.get((c.pc,k))
  if t is not None and n:
   if n not in t['owners']:t['owners'].append(n)
   if n=='GameLoop':t['GameLoop_calls']+=1
   elif n=='MarioSourcePowerupCollision':assert c.x==5;t['collisions']+=1
   elif n=='Cv3CollectPickupGate':assert c.x==5;t['collect_entries']+=1
   elif n=='ShellOrBlockDefeat'and c.x==0:t['defeats']+=1
  original(c)
 NesMPU.step=step
 try:
  for task in plan:
   scene(q,v,task);t=dict(name=task['name'],kind=task['kind'],owners=[],GameLoop_calls=0,collisions=0,collect_entries=0,defeats=0,heart_before=q.get('Cv3Hearts',v-1),health_before=q.get('Cv3Health',v-1),power_before=q.get('Cv3Power',v-1),sub_before=q.get('Cv3Subweapon',v-1),types=[],allocations=0,heart_writes=[])
   first=None;placed=task.get('watch',False);watchxy=None
   for age in range(task['limit']+1):
    bits=buttons(task,age,q,t)
    if task['kind']=='use'and not placed:
     if task.get('melee')and 3<=q.get('Cv3AttackAge')<=10:
      target(q,89 if v==1 else 92,184);placed=True
     elif task['shot']>0:
      for i in range(4):
       if q.get('Cv3ShotType',i)==task['shot']and q.get('Cv3ShotPage',i)==0 and 100<=q.get('Cv3ShotX',i)<=220 and 40<=q.get('Cv3ShotY',i)<=208:
        if first is None:first=age
        if age>=first+4:target(q,q.get('Cv3ShotX',i)-6,min(184,q.get('Cv3ShotY',i)-8));placed=True;break
    q.set('SavedJoypadBits',bits);_,writes=q.invoke('GameLoop')
    assert q.get('MmDeathFlag')==q.get('Cv3HurtAge')==q.get('Cv3Invul')==0,(v,task,age,'hurt',q.get('Cv3Health',v-1))
    for w in writes:
     if address(b,'Cv3ShotType')<=w['address']<address(b,'Cv3ShotType')+4 and w['value']:
      t['allocations']+=1
      if w['value']not in t['types']:t['types'].append(w['value'])
     if w['address']==address(b,'Cv3Hearts')+v-1:t['heart_writes'].append([age,w['value'],w['pc'],w['bank']])
     if w['address']==address(b,'AvStopwatch'):t.setdefault('watch_writes',[]).append([age,w['value'],w['pc'],w['bank']])
    if q.get('AvStopwatch'):
     t['watch_ticks']=t.get('watch_ticks',0)+1;xy=[q.get('Enemy_X_Position'),q.get('Enemy_Y_Position')]
     assert watchxy is None or xy==watchxy;watchxy=xy
    if q.get('Cv3FrozenTimer'):
     t['frozen_ticks']=t.get('frozen_ticks',0)+1;assert q.get('AvFrozen')and q.get('Enemy_ID')==6
    if q.get('Cv3Climb'):
     t['climb_seen']=True;t['climb_min_y']=min(t.get('climb_min_y',176),q.get('Player_Y_Position'))
     if q.get('Cv3Climb')==3:t.setdefault('attached_at',age);t.setdefault('ceiling_x',[]).append(q.get('Player_X_Position'))
    if q.get('Cv3Bat'):
     t.setdefault('bat_states',[])
     if not t['bat_states']or t['bat_states'][-1]!=q.get('Cv3Bat'):t['bat_states'].append(q.get('Cv3Bat'))
     t['max_x']=max(t.get('max_x',64),q.get('Player_X_Position'));t['min_y']=min(t.get('min_y',176),q.get('Player_Y_Position'))
    if task['kind']=='collect'and t['collisions']:
     assert t['collisions']==t['collect_entries']==1 and q.get('InvPickup',5)==0 and q.get('Cv3PickupVariant',5)==0 and q.get('PlayerStatus')==1 and q.get('GuestPowerupActive')==0
     if task['item']==208:assert q.get('Cv3Health',v-1)==min(64,t['health_before']+16)
     elif task['item']==212:assert q.get('Cv3Power',v-1)==min(2,t['power_before']+1)
     else:assert q.get('Cv3Subweapon',v-1)==task['item']-208 and q.get('Cv3Hearts',v-1)==min(99,t['heart_before']+5)
     break
    if task['kind']=='heart'and q.get('Cv3DropType')==0:
     assert q.get('Cv3Hearts',v-1)==min(99,t['heart_before']+task['item']);break
    if age==task['limit']:
     assert all(q.get('Cv3ShotType',i)==0 for i in range(4))and q.get('Cv3AttackAge')==q.get('Cv3Bat')==q.get('Cv3Climb')==q.get('AvStopwatch')==0,(v,task,'cleanup',t)
     if task['kind']=='use':
      assert placed
      if task.get('ice'):assert t.get('frozen_ticks',0)>=100 and not q.get('Cv3FrozenTimer')
      elif task.get('watch'):
       assert t.get('watch_ticks')==watch_expected and q.get('Enemy_X_Position')!=watchxy[0],(task,t,q.get('Enemy_X_Position'),watchxy)
       if watch_expected!=180:t['source_contract_failure']={'expected_active_updates':180,'observed_active_updates':watch_expected,'reason':'Two distinct source decrement owners per completeGameLoop; native strict180 case not qualified.'}
      else:assert t['defeats']>0,(v,task,'no real defeat',t)
      assert task['shot']==0 or task['shot']in t['types']
      assert t['allocations']==task.get('allocations',0),(v,task,'allocations',t)
      assert q.get('Cv3Hearts',v-1)==t['heart_before']-task.get('cost',0),(v,task,'cost',t,q.get('Cv3Hearts',v-1))
     elif task['kind']=='wall':assert t.get('climb_seen')and t['climb_min_y']<160 and q.get('Player_State')==0,(task,t)
     elif task['kind']=='ceiling':assert t.get('ceiling_x')and max(t['ceiling_x'])>min(t['ceiling_x'])and q.get('Player_State')==0,(task,t)
     elif task['kind']=='bat':assert t.get('bat_states')==[1,2,3]and t['max_x']>100 and t['min_y']<150 and q.get('Player_State')==0 and q.get('Cv3Hearts',v-1)<t['heart_before'],(task,t)
     break
   else:raise AssertionError((v,task,'timeout',t))
   t.update(age=age,heart_after=q.get('Cv3Hearts',v-1),health_after=q.get('Cv3Health',v-1),power_after=q.get('Cv3Power',v-1),sub_after=q.get('Cv3Subweapon',v-1));out.append(t)
 finally:NesMPU.step=original
 return dict(passed=v!=1 or watch_expected==180,source_CPU_only=True,ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),variant=v,known_watch_duration_failure=v==1 and watch_expected!=180,cases=out,GameLoop_calls=1+sum(x['GameLoop_calls']for x in out),limits='Fresh finite complete GameLoop CPU only; no native interrupts/PPU/APU/Lua/cadence/waveform or full route. Mature actors and aligned legal enemy target are disclosed; no tested upgrade/heart/health/transform/projectile outcome seeds.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--family',choices=list(VARIANTS),required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',default=SHA);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-only',action='store_true');a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve();assert sha(a.rom)==a.expected_sha256==SHA and not a.output.exists();b=scoped_load(a.rom);v=VARIANTS[a.family];plan=plans(v);proof=source_campaign(b,v,plan);a.output.mkdir(parents=True);put(a.output/'source-controls.json',proof);print(json.dumps(dict(passed=proof['passed'],family=a.family,calls=proof['GameLoop_calls'],cases=len(plan))))

if __name__=='__main__':main()
