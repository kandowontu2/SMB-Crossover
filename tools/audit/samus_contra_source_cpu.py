"""Actual assembled Samus Wave page arithmetic and unchanged shot controls."""
from pathlib import Path
import argparse,hashlib,json,itertools
from vehicles_mike_mac_audit_cpu_v1 import Arena
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','page-only','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(exist_ok=False);old,new=load(a.baseline),load(a.candidate)
 def init(b,center,slot,polarity,direction=3,typ=3,scroll=None):
  q=Arena(b);q.put(SelectedCharacter=2,ScreenLeft_X_Pos=(scroll if scroll is not None else center-120)&255,ScreenLeft_PageLoc=(scroll if scroll is not None else center-120)//256,SmSlot=slot)
  for n,v in [('SmShotType',typ),('SmShotAge',0),('SmShotDir',direction),('SmShotX',center&255),('SmShotPage',center//256),('SmShotY',230),('SmShotCenter',center&255 if direction==3 else 230),('SmShotPolarity',polarity)]:q.set(n,v,slot)
  return q
 q=init(old,766,2,1);q.set('SmShotAge',2,2);q.set('SmShotY',140,2);q.call('SamusWeapons::Move',x=2)
 assert(q.get('SmShotType',2),q.get('SmShotX',2),q.get('SmShotPage',2))==(0,4,2)
 failure=dict(center=766,age=2,expected_world=772,actual_world=q.get('SmShotX',2)+256*q.get('SmShotPage',2),first_wrong_erase=next(z for z in q.m.trace if z['address']==address(old,'SmShotType')+2),trace=q.m.trace)
 wave=new['raw'][location(new,'SamusWeapons::WaveTable'):location(new,'SamusWeapons::WaveTable')+256]
 rows=[];cross=0
 for low,slot,polarity in itertools.product(range(256),range(3),range(2)):
  center=768+low;q=init(new,center,slot,polarity);lastpage=center//256
  for age in range(1,47):
   q.set('SmShotAge',age,slot);c=q.call('SamusWeapons::Move',x=slot)
   off=wave[age-1];off=off-256 if off>=128 else off;expected=center+(off if polarity else -off)
   got=q.get('SmShotX',slot)+256*q.get('SmShotPage',slot)
   assert got==expected and q.get('SmShotType',slot)==3,(low,slot,polarity,age,got,expected)
   assert c.x==slot
   if expected//256!=lastpage:cross+=1
   lastpage=expected//256
  rows.append(dict(center=center,slot=slot,polarity=polarity,updates=46))
 controls=0
 for center,slot,polarity,direction,typ in itertools.product([512,513,520,639,640,759,766,767],range(3),range(2),[1,2,3],[1,2,3]):
  if typ==3 and direction==3:continue
  qo,qn=init(old,center,slot,polarity,direction,typ),init(new,center,slot,polarity,direction,typ)
  for age in range(1,8):
   for q in [qo,qn]:q.set('SmShotAge',age,slot)
   co,cn=qo.call('SamusWeapons::Move',x=slot),qn.call('SamusWeapons::Move',x=slot)
   assert qo.m[:32768]==qn.m[:32768] and(co.a,co.x,co.y,co.p,co.sp)==(cn.a,cn.x,cn.y,cn.p,cn.sp)
   controls+=1
 edge=[]
 for center,scroll,pol in itertools.product([767,768,769],[632,648,752,768,784],range(2)):
  q=init(new,center,2,pol,scroll=scroll)
  for age in [1,2,4,6,8]:
   q.set('SmShotType',3,2);q.set('SmShotAge',age,2);q.call('SamusWeapons::Move',x=2)
   off=wave[age-1];off=off-256 if off>=128 else off;expected=center+(off if pol else -off)
   assert q.get('SmShotX',2)+256*q.get('SmShotPage',2)==expected
   visible=0<=expected-scroll<256;assert bool(q.get('SmShotType',2))==visible
   edge.append(dict(center=center,scroll=scroll,polarity=pol,age=age,visible=visible))
 # Full production SamusWeapons, not only the outlined Move. Retain the
 # intermediate page-only proposal to isolate its wrong terrain dispatch.
 terrain=[];page_only=load(a.page_only);wrong=[]
 def arena(b,slot,mode,typ=3):
  q=init(b,254,slot,1,typ=typ,scroll=120)
  q.put(CrossoverBehaviorVersion=mode,PlayerStatus=2 if mode==0 else 1,GameEngineSubroutine=8,PlayerFacingDir=1,Player_Y_Position=176,Player_Y_HighPos=1)
  q.set('InvOwnedLo',145,2);q.set('SmShotY',172,slot);q.m[address(b,'Block_Buffer_2')+112]=192
  return q
 for mode,slot in itertools.product(range(2),range(3)):
  qo,qn=arena(page_only,slot,mode),arena(new,slot,mode)
  for tick in range(1,8):
   qo.call('SamusWeapons');qn.call('SamusWeapons')
   assert qn.get('SmShotType',slot)==3 and qn.get('SmShotImpact',slot)==0
   if tick==3 and slot!=0:
    assert qo.get('SmShotImpact',slot)==3
    wrong.append(dict(mode=mode,slot=slot,first_wrong_impact=next(z for z in qo.m.trace if z['address']==address(page_only,'SmShotImpact')+slot and z['value']==3)))
  assert qo.get('SmShotType',slot)==(3 if slot==0 else 0)
  terrain.append(dict(mode=mode,slot=slot,updates=7,expected='Wave remains live across original question-block terrain'))
 # Both pinned games reject terrain for Wave only; ordinary beams retain it.
 for mode,slot,typ in itertools.product(range(2),range(3),[1,2]):
  q=arena(new,slot,mode,typ)
  for tick in range(1,7):q.call('SamusWeapons')
  assert q.get('SmShotType',slot)==0
  terrain.append(dict(mode=mode,slot=slot,type=typ,expected='Non-Wave retains native terrain impact'))
 family=[]
 # Actual mushroom collection + complete power-up routine establishes the
 # base ownership bit, rather than pretending a fresh Hard mushroom is MG.
 for ch,variant in [(2,0),(3,0),(3,1)]:
  q=Arena(new);q.put(SelectedCharacter=ch,CrossoverBehaviorVersion=1,PlayerStatus=0,GameEngineSubroutine=8,BillVariant=variant)
  q.set('InvPickupOwner',ch,5);q.set('InvPickup',0,5);q.call('InventoryCollect',x=5)
  for _ in range(60):q.call('GuestPowerupUpdate')
  c=q.call('RemainingPower');assert q.get('InvOwnedLo',ch)==(129 if ch==2 else 1)and q.get('PlayerStatus')==1 and c.a==(1 if ch==2 else 0)
  family.append(dict(kind='real_mushroom_component',character=ch,variant=variant,owned=q.get('InvOwnedLo',ch),power=c.a))
 for variant,mode,power in itertools.product(range(2),range(2),range(3)):
  q=Arena(new);q.put(SelectedCharacter=3,CrossoverBehaviorVersion=mode,PlayerStatus=power,BillVariant=variant)
  if mode:q.set('InvOwnedLo',1,3)
  c=q.call('GuestInjuryStatus');assert c.a==(0 if mode else power)
  family.append(dict(kind='source_contact_admission',variant=variant,mode=mode,power=power,result=c.a))
 # getRealSpeed truncates Flash int before Q8 quantization. Rapid2 source
 # retains Rapid1, so both independent0.1 bonuses are included.
 for variant,face,(gun,typ,sel,base),rapid in itertools.product(range(2),[1,2],[('normal',11,0,288),('machine',11,4,315),('spread',12,5,333),('laser',42,2,333),('flare',43,3,211)],range(3)):
  q=Arena(new);q.put(SelectedCharacter=3,CrossoverBehaviorVersion=1,PlayerStatus=1,BillVariant=variant,PlayerFacingDir=face,Player_X_Position=100,Player_Y_Position=176,Player_Y_HighPos=1)
  q.set('InvOwnedLo',1|(2 if rapid else 0)|(64 if rapid==2 else 0)|(1<<sel if sel else 0),3);q.set('InvSelected',sel,3);q.set('RgShotType',typ,2);q.call('BillSourceProjection',x=2)
  got=q.get('RgShotVXLo',2)+256*q.get('RgShotVXHi',2);want=(int(base*(10+rapid)/10)*256+60)//120
  assert got==(want if face==1 else -want)&65535 and q.get('RgShotVYLo',2)==q.get('RgShotVYHi',2)==0
  family.append(dict(kind='Contra_source_rapid_speed',variant=variant,face=face,gun=gun,rapid=rapid,Q8_speed=want))
 # Hard first Down crouches; fresh second Down requires Morph. Easy enters
 # its intrinsic ball immediately. Empty terrain is a declared component.
 for mode,morph in itertools.product(range(2),range(2)):
  q=Arena(new);q.put(SelectedCharacter=2,CrossoverBehaviorVersion=mode,PlayerStatus=1,GameEngineSubroutine=8,Player_State=0,Player_Y_Position=176,Player_Y_HighPos=1,SavedJoypadBits=4)
  q.set('InvOwnedLo',129|(2 if morph else 0),2);q.call('SamusMovement')
  assert(q.get('SmCrouch'),q.get('SmBall'))==((1,0)if mode else(0,1))
  q.set('SavedJoypadBits',0);q.call('SamusMovement');q.set('SavedJoypadBits',4);q.call('SamusMovement')
  assert q.get('SmBall')==(1 if not mode or morph else 0)
  family.append(dict(kind='Samus_first_second_Down',mode=mode,Morph_owned=morph,ball=q.get('SmBall')))
 (a.output/'preserved-failure.json').write_text(json.dumps(failure,indent=2));(a.output/'preserved-terrain-failures.json').write_text(json.dumps(wrong,indent=2));(a.output/'cases.json').write_text(json.dumps(rows+edge+terrain+family,separators=(',',':')))
 proof=dict(passed=True,parent_ROM_sha256=sha(a.baseline),ROM_sha256=sha(a.candidate),page_only_negative_ROM_sha256=sha(a.page_only),upward_wave_sequences=len(rows),upward_actual_CPU_updates=len(rows)*46,page_crossings=cross,unchanged_horizontal_wave_and_nonwave_controls=controls,viewport_controls=len(edge),full_production_terrain_cases=len(terrain),preserved_terrain_failures=len(wrong),family_source_components=len(family),tool_sha256=sha(Path(__file__)),scope='Actual assembled routines; independent signed source-sinusoid offsets around a full world center using unchanged quantized WaveTable. Full beam/block components, original0/+1 mushroom collection, Contra native getRealSpeed/contacts and Samus Down admission are bounded checks. Native actor/input/interrupt/render qualification is separate.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
