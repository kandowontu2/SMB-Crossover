"""Compiled private Rogue weapons: finite CPU contracts, never native coverage."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_lifecycle_controls_v1 as life
import rogue_dawn_host_lifecycle_edges_v1 as edges
import rogue_dawn_map_v1 as ref
import rogue_dawn_actor_item_proposal_v1 as original
import prepare_rogue_dawn_art_v1 as art
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import run,app,registers,cleanwrites
O=R/'build/rogue-dawn-host-weapons-v1';get,put=life.get,life.put

def call(m,name,**kw):return life.d.call(m,name,sp=kw.pop('sp',224),**kw)
def field(m,name,v,i=0):m[address(m.bundle,name)+i]=v
def shot(m,slot=0xd0,action=1,wx=164,y=180,frame=40):
 for n,v in [('RdWAction',action),('RdWX',wx&255),('RdWHi',wx>>8),('RdWY',y),('RdWRadiusX',2),('RdWRadiusY',2),('RdWVX',4),('RdWVY',0),('RdWFrame',frame),('RdWAnim',0x1b),('RdWReset',0x1b),('RdWDelay',1),('RdWOnScreen',1)]:field(m,n,v,slot)
 put(m,RdSlot=slot)
def target(m,ident=6,wx=160,y=176):
 for n,v in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_PageLoc',wx>>8),('Enemy_X_Position',wx&255),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_BoundBoxCtrl',9),('EnemyOffscrBitsMasked',0)]:field(m,n,v)
 put(m,ObjectOffset=0)

def main():
 b=life.d.old.scoped_load(O/'candidate.nes');parent=life.d.old.scoped_load(life.O/'candidate.nes');checks={};minimum=255
 proof=dict(passed=False,source_CPU_only=True,native_run=False,ROM=ref.binding(O/'candidate.nes'),checks=checks)
 try:
  rows=[]
  for page,x,vx,vy,y in itertools.product([0,1,255],[0,2,252,255],[0,4,252],[0,2,254],[32,180]):
   m=life.make(b);shot(m,wx=page*256+x,y=y);put(m,RdSlot=0xd0);field(m,'RdWVX',vx,0xd0);field(m,'RdWVY',vy,0xd0)
   c,l,tr=call(m,'RdWxMove');minimum=min(minimum,l)
   sx=vx-256 if vx&128 else vx;sy=vy-256 if vy&128 else vy
   assert get(m,'RdWX',0xd0)+256*get(m,'RdWHi',0xd0)==(page*256+x+sx)&65535
   assert get(m,'RdWY',0xd0)==(y+sy)&255 and c.p&1
   rows.append(c.processorCycles)
  checks['signed_full_page_motion']=dict(cases=len(rows),CPU=sorted(set(rows)))
  rows=[]
  for camera,delta,y in itertools.product([0,249,256],[-9,-8,-1,0,255,256,263,264],[23,24,239,240]):
   m=life.make(b);put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
   shot(m,wx=(camera+delta)&65535,y=y);call(m,'RdWxViewport')
   assert get(m,'RdWOnScreen',0xd0)==int(-8<=delta<=263 and 24<=y<=239)
   rows.append([camera,delta,y])
  checks['declared_SMB_viewport_adaptation']=len(rows)
  table={6:2,0:4,3:4,14:4,15:4,16:4,13:4,18:4,5:8,17:8};rows=[]
  for ident in range(256):
   m=life.make(b);target(m,ident);c,l,tr=call(m,'RdWxActorEligible',x=0)
   assert bool(c.p&1)==(ident in table)
   if ident in table:assert c.a==table[ident]
   rows.append(ident)
  checks['all_native_IDs_no_default_HP']=dict(cases=len(rows),approved_table=table)
  rows=[]
  for flag,state,high,slot in itertools.product([0,1,2,128],[0,32],[0,1,2],range(6)):
   m=life.make(b);target(m)
   for n,v in [('Enemy_Flag',flag),('Enemy_State',state),('Enemy_Y_HighPos',high),('Enemy_ID',6)]:field(m,n,v,slot)
   c,l,tr=call(m,'RdWxActorEligible',x=slot)
   assert bool(c.p&1)==(slot<5 and flag==1 and state==0 and high==1)
   rows.append(c.processorCycles)
  checks['real_slot_flag_state_high_rejections']=len(rows)
  # Compare source DA92 scalar arithmetic, stopping at the real original
  # death continuation. The host deliberately maps ordinary SMB properties;
  # it does not claim original F5D3 missile terminal admission equality.
  rows=[];raw=ref.ROM.read_bytes()
  for weapon,gear,hp in itertools.product([1,2,3,10,11],[0,64,128,192],range(1,10)):
   n=art.Memory(ref.cpu_image(raw,lower_bank=2));n[0x40e]=weapon;n[0x6878]=gear;n[0x0a]=0;n[0x40b]=hp
   original.prefix(n,0xda92,0xf60f)
   m=life.make(b);target(m);put(m,RdGear=gear);field(m,'MmEnemyHealthLo',hp)
   if weapon==3:field(m,'AvFrozen',64);field(m,'RgEnemyStun',1)
   c,l,tr=call(m,'RdWxActorContact',a=weapon,x=0);minimum=min(minimum,l)
   assert get(m,'MmEnemyHealthLo')==n[0x40b],(weapon,gear,hp,get(m,'MmEnemyHealthLo'),n[0x40b])
   dead=n[0x40b]==0
   assert bool(get(m,'Enemy_State')&32)==dead
   if not dead:assert get(m,'MmEnemyFlash')==get(m,'RgEnemyStun')==6 and get(m,'AvFrozen')==0
   rows.append([weapon,gear,hp,n[0x40b]])
  checks['actual_source_DA92_scalar_and_real_terminal_owner']=dict(cases=len(rows),case_SHA256=ref.digest(json.dumps(rows).encode()),missile_mapping='Approved SMB scalar-property adaptation; source F5D3 ordinary instant-terminal alternative is not claimed equivalent')
  rows=[]
  for clock in range(8):
   m=life.make(b);target(m);put(m,RdGear=128);field(m,'MmEnemyHealthLo',8);put(m,RdClock=clock)
   call(m,'RdWxActorContact',a=3,x=0);assert get(m,'AvFrozen')==64 and get(m,'MmEnemyHealthLo')==8
   dec=[]
   for tick in range(1,514):
    put(m,RdClock=(clock+tick)&255);before=get(m,'AvFrozen');call(m,'RdWxActorContact',a=0,x=0)
    if get(m,'AvFrozen')!=before:dec.append(tick)
    if get(m,'AvFrozen')==0:break
   assert tick==512-clock and len(dec)==64 and get(m,'RgEnemyStun')==0
   rows.append(dict(initial_clock=clock,actual_updates=tick,decrements=64))
  checks['source_64counter_8tick_freeze_schedule']=rows
  rows=[]
  for initial in range(1,7):
   m=life.make(b);target(m);field(m,'MmEnemyHealthLo',8);field(m,'MmEnemyFlash',initial);field(m,'RgEnemyStun',initial)
   for age in range(initial):
    call(m,'RdWxActorContact',a=2,x=0);assert get(m,'MmEnemyHealthLo')==8 and get(m,'MmEnemyFlash')==initial-age-1
   call(m,'RdWxActorContact',a=2,x=0);assert get(m,'MmEnemyHealthLo')==6
   rows.append(initial)
  checks['hurt_phase_refuses_contacts_until_real_phase_exit']=rows
  # Continuous real IdleLoop/GameLoop/NMI rather than fake host services.
  rows=[]
  for gear,keys,face in itertools.product([0,64,128,192,1],[64,65,72],[0,1]):
   m=life.make(b);put(m,RdGear=gear,SavedJoypadBits=keys,Left_Right_Buttons=keys&3);m[0x5c2c]=face
   states=[]
   for age in range(36):
    c,row=life.mainstep(m,first=age==0);minimum=min(minimum,row['minimum_SP'])
    states.append([get(m,'RdWAction',s)for s in[0xd0,0xe0,0xf0]])
   assert any(any(s)for s in states),(gear,keys,face,states)
   rows.append(dict(gear=gear,keys=keys,facing=face,complete_Mains=36,actions=sorted({a for s in states for a in s}),minimum_SP=row['minimum_SP']))
  checks['actual_continuous_GameLoop_source_weapon_caller']=rows
  rows=[]
  for slot in[208,224,240]:
   m=life.make(b);shot(m,slot,3,wx=128,y=128);put(m,RdGear=128);field(m,'RdWHit',1,slot)
   call(m,'RdWxUpdateSlot');assert get(m,'RdWAction',slot)==4 and get(m,'SmBombBlocksDone',(slot-208)//16)==129 and get(m,'RdWeaponColor')==0
   put(m,RdSlot=slot);call(m,'RdWxUpdateSlot');assert get(m,'SmBombBlocksDone',(slot-208)//16)==0 and get(m,'RdWeaponColor')==0
   rows.append(dict(slot=slot,Ice_impact_update_color=129,next_impact_color=0))
  checks['action_to_render_delay_preserves_Ice_impact_color_phase']=rows
  rows=[]
  for action in[8,9,10]:
   m=life.make(b);shot(m,action=action,wx=128,y=128,frame=60);field(m,'RdWAge',1,208);field(m,'RdWAnim',0x7f,208);field(m,'RdWReset',0x7f,208)
   if action==10:field(m,'RdWAnim',0x82,208);field(m,'RdWReset',0x82,208)
   states=[]
   for age in range(70):
    put(m,RdSlot=208,RdClock=age&255);call(m,'RdWxUpdateSlot');states.append(get(m,'RdWAction',208))
    if get(m,'RdWAction',208)==0:break
   assert states[-1]==0,(action,states)
   rows.append(dict(initial_action=action,actual_updates=age+1,phases=list(dict.fromkeys(states))))
  checks['genuine_current8_9_10_bomb_phase_lifetimes']=rows
  checks['unadmitted_legacy5_6_7']=dict(current_original_allocator='D150..D197 only produces8; current chain8->9->10->0 is the admitted action producer',source_old_animation37='Five actual source area tables8572+37 are404142FF; this loops and does not produceF7. Frozen weapon animation/art API does not claim old unused5/6/7 gameplay.',legacy_external_state='Not admitted by this host; no fake endflag/cleanup or expanded art is supplied for arbitrary externally seeded legacy actions.')
  proof.update(passed=True,minimum_SP=minimum,limits=['CPU source contracts only. No Mesen/native, completed physical DMA/CHR/PPU/audio or playable admission.','Typed controlled initial actor/resources are source fixtures, never earned acquisition evidence.','Ice palette1 lease, typed mature art/progression, drops/hazards/boss mappings and source audio remain open.'])
 except BaseException as e:
  proof.update(error=str(e),traceback=traceback.format_exc());raise
 finally:
  proof['bindings']=[ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',R/'src/rogue_dawn_host_weapons.s',R/'src/rogue_dawn_host_weapons_gate.s',ref.ROM]]
  (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,minimum_SP=minimum,checks={k:len(v)if isinstance(v,list)else v for k,v in checks.items()})))
if __name__=='__main__':main()
