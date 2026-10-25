"""TMNT equipment CPU component checks. Seeded RAM is not natural collection."""
from pathlib import Path
import argparse,hashlib,json,gzip
from py65.devices.mpu6502 import MPU
P=argparse.ArgumentParser();P.add_argument('--rom',type=Path,required=True);P.add_argument('--context',type=Path,required=True);P.add_argument('--output',type=Path,required=True);A=P.parse_args();O=A.output;O.mkdir(parents=True,exist_ok=False);raw=A.rom.read_bytes();S={};G={}
f=A.rom.with_suffix('.dbg');txt=f.read_text()if f.exists()else gzip.decompress(A.rom.with_suffix('.dbg.gz').read_bytes()).decode()
for line in txt.splitlines():
 if not line.startswith(('sym\t','seg\t')):continue
 z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
 if line.startswith('seg\t'):G[z['id']]=z
 elif 'val'in z:S[z['name'].strip('"')]=z

def addr(n):return int(S[n]['val'],0)
def bank(n):
 g=G[S[n]['seg']];return(int(g['ooffs'],0)+addr(n)-int(g['start'],0)-16)//8192
class Mem(list):
 def __init__(self):super().__init__([0]*65536);self.writes=[];self.banks=[126,87,88,127];self.banks[1]=87
 def page(self,w,b):
  self.banks[w]=b;list.__setitem__(self,slice(0x8000+w*8192,0xa000+w*8192),raw[16+b*8192:16+(b+1)*8192])
 def __setitem__(self,k,v):
  if isinstance(k,int):
   if k>=0x8000:raise AssertionError(('unexpected CPU ROM write',hex(k),v))
   self.writes.append((k,v));list.__setitem__(self,k,v)
   if 0x5114<=k<=0x5117:self.page(k-0x5114,v&127)
  else:list.__setitem__(self,k,v)
def setup(n):
 m=Mem()
 for i,b in enumerate([126,87,88,127]):m.page(i,b)
 for g in G.values():
  if g.get('name')=='"SMCCODE"':
   start,size,pos=(int(g[v],0)for v in ['start','size','ooffs']);m[start:start+size]=raw[pos:pos+size]
 seg=G[S[n]['seg']];window=(int(seg['start'],0)-0x8000)//8192;m.page(window,bank(n))
 for x,w in [('CurrentBank',1),('CurrentBankC',2)]:
  if x in S:m[addr(x)]=m.banks[w]|128
 def put(n,v,i=0):m[addr(n)+i]=v&255
 def get(n,i=0):return m[addr(n)+i]
 return m,put,get

def run(m,n,a=0,x=0,y=0,p=0x30):
 m[0x1fe]=0xef;m[0x1ff]=0xff;m.writes=[];c=MPU(memory=m,pc=addr(n));c.sp=0xfd;c.a=a;c.x=x;c.y=y;c.p=p
 for i in range(30000):
  if c.pc==0xfff0:return c
  c.step()
 raise AssertionError(('timeout',n,hex(c.pc),m.banks))
rows=[]
# Actual movement B dispatch rather than directly calling the retained primary helper.
for v in range(4):
 for kind in range(1,5):
  for selected in [0,1]:
   for available in range(4):
    m,w,r=setup('TnMovement')
    for n,value in [('SelectedCharacter',19),('TnVariant',v),('TnMarker',0xc9),('TnLife',2),('NumberofLives',2),('TnHealth',128),('TnEquipment',kind),('TnAmmo',20)]:w(n,value,v if n in ['TnHealth','TnEquipment','TnAmmo']else 0)
    for n,value in [('TnGearSelected',selected),('TnInputFrame',255),('TnClock',1),('TnJumpStage',8),('SavedJoypadBits',0x40),('FrameCounter',12),('PlayerFacingDir',1),('Player_Y_HighPos',1),('Player_Y_Position',176),('Player_X_Position',80)]:w(n,value)
    for i in range(3-available):w('TnShotKind',1,i)
    run(m,'TnMovement');spawned=min(available,3 if kind==2 else 1)if selected else 0
    assert r('TnAmmo',v)==20-(spawned>0),(v,kind,selected,available,'ammo',r('TnAmmo',v))
    if selected:
     assert r('TnThrow')==1 and r('TnAttack')==0 and r('TnSeq')==0x82,(v,kind,selected,available,'throw')
     assert r('TnSpawned')==spawned
    else:assert r('TnAttack')==v+5 and r('TnThrow')==0
    rows.append({'case':'movement_fire_dispatch','v':v,'kind':kind,'selected':selected,'free_slots':available,'spawned':spawned})
# Original duplicate/replacement rules, each turtle separately.
for v in range(4):
 for kind in range(1,5):
  for old in range(5):
   for ammo in [0,1,19,20,80,99]:
    for selected in [0,1]:
     m,w,r=setup('TnGiveEquipment');w('TnVariant',v)
     for i in range(4):w('TnEquipment',old if i==v else i+1,i);w('TnAmmo',ammo if i==v else 30+i,i)
     w('TnGearSelected',selected);before=[(r('TnEquipment',i),r('TnAmmo',i))for i in range(4)]
     run(m,'TnGiveEquipment',a=kind);assert(r('TnEquipment',v),r('TnAmmo',v),r('TnGearSelected'))==(kind,min(99,ammo+20)if old==kind else 20,selected if old==kind else 1)
     assert all((r('TnEquipment',i),r('TnAmmo',i))==before[i]for i in range(4)if i!=v)
     rows.append({'case':'per_turtle_original_pickup_semantics','v':v,'kind':kind,'old':old,'ammo':ammo,'selected':selected})
# Full-health/hurt reveal and late damage: freeze source-scroll identity at reveal.
for v in range(4):
 for hp in [32,127,128]:
  for kind in range(4):
   for slot in range(6):
    m,w,r=setup('TnPreparePickupDispatch');w('SelectedCharacter',19);w('TnVariant',v);w('TnHealth',hp,v);w('PowerUpType',kind,slot);w('Enemy_ID',0x2e,slot);w('Enemy_State',1,slot);w('Enemy_Y_Position',136,slot)
    run(m,'TnPreparePickupDispatch',x=slot);private=hp==128 and kind==1
    assert(r('TnPickupStamp',slot)==4)==private,(v,hp,kind,slot,private,r('TnPickupStamp',slot),r('InvPickup',slot),r('InvPickupOwner',slot),r('TnHealth',v),r('PowerUpType',slot),m.banks)
    if private:
     for tick in range(48):
      c=run(m,'TnRisePickupDispatch',x=slot);assert c.p&1
      assert r('TnEquipment',v)==0 and r('TnAmmo',v)==0
      collision=run(m,'TnPickupCollisionDispatch',x=slot);assert bool(collision.p&1)==(tick==47)
     assert r('Enemy_Y_Position',slot)==120 and r('Enemy_State',slot)==128
     w('TnHealth',64,v);c=run(m,'TnCollectEquipment',x=slot);assert c.p&1
     assert(r('TnEquipment',v),r('TnAmmo',v),r('TnHealth',v))==(4,20,64)
    rows.append({'case':'physical_reward_reveal_freeze_rise','v':v,'hp':hp,'native_kind':kind,'slot':slot,'scroll':private})
# Empty gear falls through actual movement to the original primary.
for v in range(4):
 for kind,ammo in [(0,0),(1,0),(4,0)]:
  m,w,r=setup('TnMovement')
  for n,value in [('SelectedCharacter',19),('TnVariant',v),('TnMarker',0xc9),('TnLife',2),('NumberofLives',2),('TnGearSelected',1),('TnClock',1),('TnInputFrame',255),('SavedJoypadBits',64),('FrameCounter',20),('PlayerFacingDir',1),('Player_Y_Position',176),('Player_Y_HighPos',1)]:w(n,value)
  w('TnEquipment',kind,v);w('TnAmmo',ammo,v);run(m,'TnMovement');assert r('TnAttack')==v+5 and r('TnGearSelected')==0 and r('TnEquipment',v)==0
  rows.append({'case':'empty_secondary_primary_fallback','v':v,'kind':kind})
# Native area clear persists equipment/HP; life loss clears only selected gear/ammo.
for v in range(4):
 for life in [False,True]:
  m,w,r=setup('TnEnsure'if life else'TnAreaReset')
  for n,value in [('SelectedCharacter',19),('TnVariant',v),('TnMarker',0xc9),('TnLife',3 if life else 2),('NumberofLives',2),('TnGearSelected',1)]:w(n,value)
  for i in range(4):w('TnHealth',64+i*16,i);w('TnEquipment',i+1,i);w('TnAmmo',30+i,i)
  w('TnShotKind',1);w('TnDropKind',3);run(m,'TnEnsure'if life else'TnAreaReset')
  assert r('TnGearSelected')==0 and r('TnShotKind')==0 and r('TnDropKind')==0
  for i in range(4):assert(r('TnHealth',i),r('TnEquipment',i),r('TnAmmo',i))==((128,0,0)if life and i==v else(64+i*16,i+1,30+i))
  rows.append({'case':'life_reset'if life else'area_reset','v':v})
# Every possible HUD queue offset; bounded append never touches Buffer2 offset0503.
for off in range(256):
 m,w,r=setup('TnAmmoHud');w('TnGearSelected',1);w('TnEquipment',4);w('TnAmmo',20);w('VRAM_Buffer1_Offset',off);base=addr('VRAM_Buffer1');m[base:base+400]=[0xa5]*400
 run(m,'TnAmmoHud');writes=[(a,v)for a,v in m.writes if base<=a<base+400]
 if off<78:
  assert bytes(m[base+off:base+off+7])==bytes([0x20,0x31,3,0x24,2,0,0]);assert r('VRAM_Buffer1_Offset')==off+6
 else:assert not writes and r('VRAM_Buffer1_Offset')==off
 assert all(a<0x503 for a,v in writes)
 rows.append({'case':'all_HUD_queue_offsets','offset':off})
# Native secondary damage table, all legal HP values, each identity/kind.
for v in range(4):
 for kind in range(1,5):
  for hp in range(129):
   m,w,r=setup('TnShotEnemies');w('SelectedCharacter',19);w('TnVariant',v);w('TnHealth',hp,v);w('TnGearSelected',1);w('TnEquipment',kind,v);w('TnShotKind',kind);w('TnShotX',100);w('TnShotY',100);m[0x5c6e]=0
   w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_Y_HighPos',1);w('Enemy_X_Position',92);w('Enemy_Y_Position',92);w('TnEnemyHP',99)
   run(m,'TnShotEnemies');expected=[18,20,14,17,16,16,29,32][(kind-1)*2+(hp<64)]
   assert r('TnEnemyHP')==99-expected,(v,kind,hp,r('TnEnemyHP'),expected)
   assert r('TnShotKind')==kind and m[0x5c40]==24
   rows.append({'case':'native_secondary_all_HP_damage','v':v,'kind':kind,'hp':hp,'damage':expected})
# Source drop lottery/receipts, identity-specific; actual dispatch retains caller A/X/Y/P.
for v in range(4):
 for prior in [0,23,24,25]:
  for rng in range(8):
   m,w,r=setup('TnEnemyDropDispatch');w('SelectedCharacter',19);w('TnVariant',v);w('Enemy_Flag',1,2);w('Enemy_ID',6,2);w('Enemy_X_Position',92,2);w('Enemy_Y_Position',176,2);w('TnDropCounter',prior);w('PseudoRandomBitReg',rng,1)
   c=run(m,'TnEnemyDropDispatch',a=0x63,x=2,y=0x45,p=0x71);drop=prior==24 and not rng&1
   assert(c.a,c.x,c.y,c.p&0xcf)==(0x63,2,0x45,0x71&0xcf),(c.a,c.x,c.y,c.p)
   assert r('TnDropCounter')==(0 if prior==24 else prior+1)
   assert [r('TnDropKind',i)for i in range(4)]==[0,0,0,[1,1,2,3][(rng>>1)&3]if drop else 0]
   before=r('TnDropCounter');run(m,'TnEnemyDropDispatch',x=2);assert r('TnDropCounter')==before
   rows.append({'case':'native_source_drop_lottery_and_receipt','v':v,'prior':prior,'rng':rng,'spawned':drop})
# Uncollected private actors expire at128 source updates, no inventory grant.
for v in range(4):
 for kind in [1,2,3]:
  m,w,r=setup('TnUpdateDrops');w('TnVariant',v);w('Player_Y_HighPos',1);w('Player_X_Position',20);w('Player_Y_Position',176);w('TnDropKind',kind,3);w('TnDropTimer',128,3);w('TnDropX',200,3);w('TnDropY',184,3)
  for tick in range(128):
   run(m,'TnUpdateDrops');assert(r('TnDropKind',3)==0)==(tick==127)
   assert r('TnEquipment',v)==0 and r('TnAmmo',v)==0
  rows.append({'case':'native_uncollected_128update_expiry','v':v,'kind':kind})
# Actual source-style drop overlap collects, not direct equipment grant.
for v in range(4):
 for kind in [1,2,3]:
  m,w,r=setup('TnUpdateDrops');w('TnVariant',v);w('Player_Y_HighPos',1);w('Player_X_Position',80);w('Player_Y_Position',176);w('TnDropKind',kind,3);w('TnDropTimer',128,3);w('TnDropX',88,3);w('TnDropY',184,3)
  run(m,'TnUpdateDrops');assert r('TnDropKind',3)==0 and(r('TnEquipment',v),r('TnAmmo',v),r('TnGearSelected'))==(kind,20,1)
  rows.append({'case':'native_drop_overlap_collection','v':v,'kind':kind})
# Independent original-ROM item overlap oracle (all bounds edges).
original_raw=Path('C:/NES/Teenage Mutant Ninja Turtles (USA).nes').read_bytes()
def original_cpu():
 c=MPU();c.memory[0x8000:0xc000]=original_raw[16+6*16384:16+7*16384];c.memory[0xc000:]=original_raw[16+7*16384:16+8*16384];return c
def original_run(c,pc,x=0,y=0):
 c.pc=pc;c.sp=0xfd;c.x=x;c.y=y;c.memory[0x1fe]=0xef;c.memory[0x1ff]=0xff
 for i in range(20000):
  if c.pc==0xfff0:return
  c.step()
 raise AssertionError(('original timeout',hex(c.pc)))
for pose in [0x80,0x83,0x87]:
 for dx in range(-14,15):
  for dy in range(-40,41):
   c=original_cpu();c.memory[0x440]=1;c.memory[0x445]=5;c.memory[0x570]=pose;c.memory[0x575]=0xde;c.memory[0x480]=88;c.memory[0x460]=108;c.memory[0x485]=88+dx;c.memory[0x465]=108+dy;c.memory[0x540]=2 if pose==0x83 else 0
   original_run(c,0x9b11);original_run(c,0x9ad3,x=5);want=bool(c.p&1)
   m,w,r=setup('TnDropOverlap');w('Player_X_Position',80);w('Player_Y_Position',100);w('Player_Y_HighPos',1);w('TnSeq',pose);w('RgCrouch',pose==0x83);m[0x5c19]=88+dx;m[0x5c1b]=108+dy
   got=bool(run(m,'TnDropOverlap').p&1);assert got==want,(pose,dx,dy,got,want,c.memory[8:20])
   rows.append({'case':'original_CPU_drop_overlap_edges','pose':pose,'dx':dx,'dy':dy,'overlap':got})
# Native returning boomerang behavior precedes common EF03 integration.
for v in range(4):
 for face in [1,2]:
  c=original_cpu();c.memory[0x8000:0xc000]=original_raw[16+5*16384:16+6*16384]
  for at,val in [(0x67,v),(0x73+v,3),(0xa8+v,19),(0x5b,1),(0x5c,1),(0x440+2,0x27),(0x450+2,0xc2+(face==2)),(0x410+2,2),(0x630+2,10),(0x480,128),(0x460,128),(0x480+2,128),(0x460+2,128),(0x4e0+2,251 if face==2 else 5)]:c.memory[at]=val
  m,w,r=setup('TnUpdateShot');w('TnVariant',v);w('TnEquipment',3,v);w('TnAmmo',19,v);w('TnGearSelected',1);w('Player_X_Position',120);w('Player_Y_Position',120);w('Player_Y_HighPos',1);w('TnShotKind',3);w('TnShotFace',face);w('TnShotX',128);w('TnShotY',128);w('TnShotVX',251 if face==2 else 5);m[0x5c6e]=0
  for tick in range(90):
   original_run(c,0xfdab,x=2)
   if c.memory[0x442]:original_run(c,0xef03,x=2)
   run(m,'TnUpdateShot');alive=bool(c.memory[0x442]);assert alive==bool(r('TnShotKind')),(v,face,tick,'catch timing',alive,r('TnShotKind'))
   if alive:
    old=tuple(c.memory[at+2]for at in[0x480,0x490,0x4e0,0x4f0]);new=(r('TnShotX'),r('TnShotFrac'),r('TnShotVX'),r('TnShotVXLo'));assert old==new,(v,face,tick,old,new)
   else:break
  assert not alive and r('TnAmmo',v)==20 and c.memory[0xa8+v]==20
  rows.append({'case':'original_CPU_boomerang_trajectory_and_catch','v':v,'face':face,'catch_update':tick+1})
# Original uncapped return after a duplicate99 refill, including valid three-digit HUD.
for v in range(4):
 m,w,r=setup('TnRestoreBoomerang');w('TnVariant',v);w('TnEquipment',3,v);w('TnAmmo',99,v)
 for i in range(3):run(m,'TnRestoreBoomerang')
 assert r('TnAmmo',v)==102
 rows.append({'case':'three_boomerang_refund_after99_refill','v':v,'ammo':102})
for ammo in range(256):
 m,w,r=setup('TnAmmoHud');w('TnGearSelected',1);w('TnEquipment',3);w('TnAmmo',ammo);m[0x5c7f]=255
 run(m,'TnAmmoHud');base=addr('VRAM_Buffer1');digits=list(m[base+3:base+6]);assert digits==[ammo//100 if ammo>=100 else 0x24,(ammo//10)%10,ammo%10],(ammo,digits)
 rows.append({'case':'all_u8_ammo_HUD_digits','ammo':ammo,'digits':digits})
# Source original duplicate refill while three boomerangs remain in flight.
for v in range(4):
 c=original_cpu();c.memory[0x67]=v;c.memory[0x73+v]=3;c.memory[0xa8+v]=98;c.memory[0x442]=7;c.memory[0x480]=80;c.memory[0x460]=100
 c.pc=0x96e3;c.sp=0xfd;c.x=2;c.memory[0x1fe]=0xef;c.memory[0x1ff]=0xff
 for step in range(20000):
  if c.pc==0xcef0:break
  c.step()
 else:raise AssertionError('original refill timeout')
 assert c.memory[0xa8+v]==99
 for i in [2,3,4]:
  c.memory[0x440+i]=0x27;c.memory[0x480+i]=80;c.memory[0x460+i]=100;original_run(c,0xfdc8,x=i)
 assert c.memory[0xa8+v]==102
 rows.append({'case':'original_CPU_refill99_then_three_returns102','v':v})
# Every frozen/duplicate updater admission leaves a drop timer unchanged.
for gate in ['timer','engine','death','cadence','duplicate']:
 m,w,r=setup('TnAllWeapons');w('SelectedCharacter',19);w('GameEngineSubroutine',8);w('TnUpdateTick',1);w('TnDropKind',1);w('TnDropTimer',128);w('TnDropX',200);w('TnDropY',160);w('Player_Y_HighPos',1);w('FrameCounter',22)
 if gate=='timer':w('TimerControl',1)
 if gate=='engine':w('GameEngineSubroutine',7)
 if gate=='death':w('MmDeathFlag',1)
 if gate=='cadence':w('TnUpdateTick',0)
 if gate=='duplicate':m[0x5c7c]=22;m[0x5c7d]=1
 run(m,'TnAllWeapons');assert r('TnDropTimer')==128 and r('TnDropKind')==1
 rows.append({'case':'native_update_pause_and_duplicate_admission','gate':gate})
# Mapped host boss hook always resets the source count and grants no gear.
for v in range(4):
 m,w,r=setup('TnEnemyDropDispatch');w('SelectedCharacter',19);w('TnVariant',v);w('TnDropCounter',23);w('Enemy_Flag',1);w('Enemy_ID',0x2d)
 run(m,'TnEnemyDropDispatch');assert r('TnDropCounter')==0 and all(r('TnDropKind',i)==0 for i in range(4))
 rows.append({'case':'mapped_boss_defeat_drop_hook_counter_clear','v':v})
# Native source D5/D6/D7 full animation state, including FE retained-last-pose update.
for kind in [1,2,3,4]:
 for v in range(4):
  c=original_cpu();c.memory[0x572]=[0xd7,0xd7,0xd6,0xd5][kind-1];c.memory[0x422]=3
  m,w,r=setup('TnAdvanceShotAnimation');w('TnShotKind',kind);w('TnShotTimer',3);w('TnVariant',v)
  for tick in range(128):
   original_run(c,0x8010,x=2);run(m,'TnAdvanceShotAnimation')
   old=tuple(c.memory[at+2]for at in[0x400,0x410,0x420]);new=(r('TnShotAnim'),r('TnShotPhase'),r('TnShotTimer'));assert old==new,(kind,v,tick,old,new)
   rows.append({'case':'original_CPU_secondary_animation_state128','v':v,'kind':kind,'tick':tick,'pose':new[0],'phase':new[1],'timer':new[2]})
# Actual original damage-context leaf, including Select/replacement/last ammo.
context=json.loads(A.context.read_text());assert context['source_ROM_sha256']==hashlib.sha256(original_raw).hexdigest()
for q in context['rows']:
 v=q['turtle'];m,w,r=setup('TnShotEnemies');w('SelectedCharacter',19);w('TnVariant',v);w('TnHealth',q['hp'],v);w('TnGearSelected',q['selected']);w('TnEquipment',q['current_equipment'],v);w('TnShotKind',q['inflight_kind']);w('TnShotX',100);w('TnShotY',100);m[0x5c6e]=0;w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_Y_HighPos',1);w('Enemy_X_Position',92);w('Enemy_Y_Position',92);w('TnEnemyHP',99)
 run(m,'TnShotEnemies');assert r('TnEnemyHP')==99-q['damage'],(q,r('TnEnemyHP'))
 rows.append({'case':'original_CPU_inflight_current_damage_context','original':q})
for v in range(4):
 for kind in range(1,5):
  m,w,r=setup('TnMovement')
  for n,value in [('SelectedCharacter',19),('TnVariant',v),('TnMarker',0xc9),('TnLife',2),('NumberofLives',2),('TnGearSelected',1),('TnClock',1),('TnInputFrame',255),('SavedJoypadBits',64),('FrameCounter',20),('PlayerFacingDir',1),('Player_Y_Position',176),('Player_X_Position',80),('Player_Y_HighPos',1)]:w(n,value)
  w('TnHealth',128,v);w('TnEquipment',kind,v);w('TnAmmo',1,v);run(m,'TnMovement');assert r('TnGearSelected')==0 and r('TnEquipment',v)==0 and r('TnAmmo',v)==0
  m.page(1,bank('TnShotEnemies'));w('CurrentBank',bank('TnShotEnemies')|128);m[0x5c6e]=0;w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_Y_HighPos',1);w('Enemy_X_Position',r('TnShotX')-8);w('Enemy_Y_Position',r('TnShotY')-8);w('TnEnemyHP',99)
  run(m,'TnShotEnemies');assert r('TnEnemyHP')==99-[7,9,7,15][v]
  rows.append({'case':'actual_B_last_ammo_inflight_primary_damage_fallback','v':v,'kind':kind})
# Full original accepted-hit consumption semantics, lethal and nonlethal.
for q in context['accepted_hits']:
 v=q['turtle'];kind=q['equipment'];m,w,r=setup('TnShotEnemies');w('SelectedCharacter',19);w('TnVariant',v);w('TnHealth',q['hp'],v);w('TnGearSelected',q['selected']);w('TnEquipment',kind,v);w('TnShotKind',kind);w('TnShotX',100);w('TnShotY',100);m[0x5c6e]=0;w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_Y_HighPos',1);w('Enemy_X_Position',92);w('Enemy_Y_Position',92);w('TnEnemyHP',q['target_HP'])
 run(m,'TnShotEnemies');assert(r('TnShotKind')==0)==q['projectile_erased'],(q,r('TnShotKind'))
 if not q['defeated']:assert r('TnEnemyHP')==q['remaining_HP']
 rows.append({'case':'original_CPU_full_accepted_hit_consumption','original':q})
counts={}
for q in rows:counts[q['case']]=counts.get(q['case'],0)+1
(O/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');proof={'passed':True,'ROM_sha256':hashlib.sha256(raw).hexdigest(),'counts':counts,'scope':'Isolated real6502 components with seeded incoming RAM. Does not certify natural collection, native pixel output or campaign clear.'};(O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
