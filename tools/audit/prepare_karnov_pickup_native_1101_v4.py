"""Controller-only first earned Karnov mushroom, no object/state injection."""
from pathlib import Path
import json,sys
import prepare_karnov_opening_native_1101_v1 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)


def main():
    prepare=P.prepare
    def adapted(output,rom,t,refs,**kw):
        b=scoped_load(rom)
        names=['KrPickupPrepareThunk','KrPickupCollectThunk','PowerUpType','InvPickupOwner']
        t=''.join('L['+json.dumps(n)+']='+str(address(b,n))+'\n'for n in names)+'''local pickupPrepares,pickupContacts,pickupFrames=0,0,0
local sawRising,sawMature,sawOwner,sawErased=false,false,false,false
local pickupSlot,pickupX,pickupY,firstHeadTick,lastPulse=nil,nil,nil,nil,-100
local pulse=0
'''+t
        t=once(t,'source_weapons=weaponTicks,','source_weapons=weaponTicks,pickup_prepares=pickupPrepares,pickup_contacts=pickupContacts,pickup_frames=pickupFrames,rising_seen=sawRising,mature_seen=sawMature,source_owner_seen=sawOwner,erased_seen=sawErased,source_health=kr(0x68),source_weapon=kr(0x65),pickup_X=pickupX,pickup_Y=pickupY,')
        t=once(t,'local function route()', '''emu.addMemoryCallback(function()if raw(L.KrPickupPrepareThunk)==3 then pickupPrepares=pickupPrepares+1;firstHeadTick=updates end end,emu.callbackType.exec,L.KrPickupPrepareThunk)
emu.addMemoryCallback(function()if raw(L.KrPickupCollectThunk)==3 then pickupContacts=pickupContacts+1 end end,emu.callbackType.exec,L.KrPickupCollectThunk)
local function route()''')
        lo=t.index(' if updates<=40 then');hi=t.index(' if updates%20==0',lo)
        t=t[:lo]+''' local item=nil
 for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then item=i;break end end
 if item then
  pickupSlot=item;pickupFrames=pickupFrames+1
  pickupX=r('Enemy_X_Position',item)+256*r('Enemy_PageLoc',item);pickupY=r('Enemy_Y_Position',item)
  if r('InvPickupOwner',item)==34 then sawOwner=true end
  if r('Enemy_State',item)&128==0 then sawRising=true else sawMature=true end
 elseif pickupSlot then sawErased=true end
 if updates<=20 then assert(x==startX,'No idle drift');pad={}
 elseif item then
  local target=math.min(pickupX-8,414)
  if x<target-1 then pad={right=true}elseif x>target+1 then pad={left=true}else pad={}end
 elseif pickupPrepares>0 then pad={}
 elseif x<328 then
  local near=false
  for i=0,5 do
   if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)==6 and r('Enemy_State',i)&32==0 then
    local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x;if dx>0 and dx<88 then near=true end
   end
  end
  pad={right=true,a=near and r('Player_State')==0}
 else
  if pulse>0 then pulse=pulse-1;pad={a=true}
  elseif r('Player_State')==0 and updates-lastPulse>30 then lastPulse=updates;pulse=3;pad={a=true}
  else pad={}end
 end
'''+t[hi:]
        t=once(t,"if updates>=240 and maxX>=220 and maxCamera>=80 and jumped and landed and maxShots>0 and shown.game and shown.game.visible and not lastMain then finish(vectors>100 and sourceTicks>100 and weaponTicks>100,'Real Karnov menu Start, original displayed body, jump/landing/source shots and opening camera crossing');return end", "if pickupPrepares>0 and pickupContacts>0 and sawRising and sawMature and sawOwner and sawErased and not lastMain then finish(kr(0x65)&3==1 and kr(0x68)&128==0,'Real head-hit block spawn, visible emergence, contact-only mushroom and earned source double shot');return end")
        t=t.replace("if updates>=650 and not lastMain then finish(false,'650 Main route bound');return end","if updates>=1400 and not lastMain then finish(false,'1400 Main pickup route bound');return end").replace("if frame>=2600 then finish(false,'2600 physical frame bound')end","if frame>=4600 then finish(false,'4600 physical frame bound')end")
        t=once(t,"..' y='..y)","..' y='..y..' source65='..kr(0x65)..' source68='..kr(0x68)..' prepare='..pickupPrepares..' contacts='..pickupContacts)")
        t=t.replace('Combat, health, earned gear, source audio and complete1-1 remain unimplemented or unqualified; not nightly admission.','This route tests a real block-emerged first mushroom and source double-shot grant. Later options, combat, source audio and full1-1 are not qualified here.')
        kw['scope']='Controller-only cold Select/Start into1-1, avoid the first goomba, head-hit the real first powerup block, observe emergence, then collect by real body contact. No RAM/code/object injection. Four PNG cap. Later option/audio/full-stage and native projectile combat remain separate.'
        kw['timeout']=200
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)
    P.prepare=adapted;P.main()


if __name__=='__main__':main()
