"""Earn real CV3 injury then D0 restoration in the same finite source campaign."""
from pathlib import Path
import hashlib
import current_cv3_powerups_prepare_v1 as base
from current_link_simon_powerups_prepare_v1 import setup,target
from check_tmnt_render_oa import address,location

def plans(v):
 original=base.plans(v);assert original[0]['item']==208
 original[0]=dict(original[0],capture=False)
 return [dict(kind='injury',item=0,name='real-hard-Goomba-contact-deficit',limit=160),dict(kind='collect',item=208,name='health-earned-from-real-contact',limit=90,healing_deficit=True)]+original

def source_campaign(b,v,plan,watch_expected=180):
 assert plan[0]['kind']=='injury'and plan[1].get('healing_deficit')
 original_scene=base.scene;prefix=None;health_writes=[];marker=''
 def intercepted(q,variant,task):
  nonlocal prefix,marker
  if task.get('healing_deficit'):
   assert prefix is None and q.get('Cv3Health',v-1)==64 and q.get('Cv3Hearts',v-1)==10
   bound=q.invoke
   def observed(name,*args,**kwargs):
    c,writes=bound(name,*args,**kwargs)
    if name=='GameLoop':
     for w in writes:
      if w['address']==address(b,'Cv3Health')+v-1:health_writes.append(dict(phase=marker,value=w['value'],pc=w['pc'],bank=w['bank']))
    return c,writes
   q.invoke=observed
   setup(q,5,dict(kind='use',item=0));target(q,72,184);marker='actual-contact-and-natural-expiry';rows=[];seen_hurt=False;seen_protection=False
   for age in range(161):
    q.set('SavedJoypadBits',0);q.invoke('GameLoop')
    row=dict(update=age+1,health=q.get('Cv3Health',v-1),hearts=q.get('Cv3Hearts',v-1),hurt=q.get('Cv3HurtAge'),protection=q.get('Cv3Invul'),injury_timer=q.get('InjuryTimer'),x=q.get('Player_X_Position'),y=q.get('Player_Y_Position'),state=q.get('Player_State'))
    assert row['health']==60 and row['hearts']==10 and not q.get('MmDeathFlag'),row
    seen_hurt|=row['hurt']>0;seen_protection|=row['protection']>0
    if age<3 or age in [14,15,62,63,64]or row['protection']==0 and row['injury_timer']==0:rows.append(row)
    if seen_hurt and seen_protection and row['hurt']==row['protection']==row['injury_timer']==0 and row['state']==0:break
   else:raise AssertionError(('Actual hurt/protection/ground did not naturally clear',rows))
   assert health_writes==[dict(phase='actual-contact-and-natural-expiry',value=60,pc=health_writes[0]['pc'],bank=82)]
   h=health_writes[0];start=address(b,'Cv3InjuryStartGate');assert start<=h['pc']<start+int(b['syms']['Cv3InjuryStartGate']['size'],0)
   at=16+h['bank']*8192+(h['pc']&8191);assert b['raw'][at:at+3]==bytes([0x99,address(b,'Cv3Health')&255,address(b,'Cv3Health')>>8])
   prefix=dict(name=plan[0]['name'],kind='injury',GameLoop_calls=age+1,heart_before=10,heart_after=10,heart_writes=[],health_before=64,health_after=60,source_actor=dict(slot=0,ID=6,x=72,y=184,player_x=64,player_y=176,Hard_mode=1),actual_health_store=h,natural_hurt16_protection64_expiry=True,states=rows,no_HP_hurt_protection_or_outcome_seed=True)
  marker=task['name'];return original_scene(q,variant,task)
 base.scene=intercepted
 try:proof=base.source_campaign(b,v,plan[1:],watch_expected=watch_expected)
 finally:base.scene=original_scene
 assert prefix and proof['passed']
 heal=proof['cases'][0];cap=proof['cases'][1]
 assert heal['health_before']==60 and heal['health_after']==64 and cap['health_before']==cap['health_after']==64
 assert [w['value']for w in health_writes]==[60,64,64]
 assert all(w['bank']==82 for w in health_writes)
 proof['cases'].insert(0,prefix);proof['GameLoop_calls']+=prefix['GameLoop_calls']
 proof.update(continuous_actual_same_arena_injury_then_D0_then_original_campaign=True,actual_hero_health_writes=health_writes,source_benefit='One real Hard Goomba collision:64->60, native recoil/16hurt/64protection and real interval injuryTimer expiry, then actualD0 min(64,60+16)=64. Original cap-onlyD0 repeated at64 remains separately verified. No HP/hurt/transform writes.',limits=proof['limits']+' All injury/healing calls execute continuously in the same actualCPU arena. This does not claim originalCV3 source-enemy damage fidelity or native/campaign success.')
 return proof
