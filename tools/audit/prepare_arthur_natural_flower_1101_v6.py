"""Cold controller-earned first flower, its emergence and original weapon event.

The v5 mushroom hypothesis was disproved: armored Arthur naturally reveals a
flower. This test changes only controller routing and read-only observations.
"""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/arthur-natural-flower-1101-v6'

def controller():
 ref=R/'tools/reference/arthur_full11_native_1101_v3.lua';t=ref.read_text()
 t=t.replace('local jumps=0','''local jumps=0
local questJump=nil
local seenItem,mature=false,false
local approach=false
local pickupCalls={}
''',1)
 marker='local function finish(passed,reason)\n'
 t=t.replace(marker,marker+''' local p=assert(io.open(OUTPUT..'powerup.json','w'));local rows={}
 for value,n in pairs(pickupCalls)do rows[#rows+1]=string.format('"%d":%d',value,n)end
 p:write(string.format('{"seen_natural_flower":%s,"mature":%s,"last_pickup":%d,"source_weapon":%d,"source_pickup_calls":{%s},"x":%d,"y":%d}',tostring(seenItem),tostring(mature),r('ArLastPickup'),r('ArR_053A'),table.concat(rows,','),wx(),r('Player_Y_Position')));p:close()
''')
 marker=' local b={right=true,b=age%21<12}\n'
 extra=''' if x>=284 or seenItem then
  b={}
  if not seenItem then
   b.right=x<328
   if x>=328 and not questJump and r('Player_State')==0 and r('ArMode')==0 then questJump=age end
  else
   if not approach then
    b.left=x>309
    if x<=309 and r('Player_State')==0 and r('ArMode')==0 then approach=true;questJump=age end
   else
    local target=r('Enemy_PageLoc',5)*256+r('Enemy_X_Position',5)
    if questJump and age-questJump>=18 and y<=136 then b.right=x<target end
    if not questJump and r('Player_State')==0 and r('ArMode')==0 then questJump=age end
   end
  end
  if questJump then
   local n=age-questJump;b.a=n<6 or(n>=18 and n<27)
   if n>=45 and r('Player_State')==0 then questJump=nil end
  end
  return b
 end
'''
 assert t.count(marker)==1;t=t.replace(marker,marker+extra)
 marker='emu.addMemoryCallback(function()\n if phase==\'play\' then mainCalls=mainCalls+1 end'
 hook='''emu.addMemoryCallback(function()
 if phase=='play' and r('CurrentBankC')==(assert(B.ArHostNativePickup)|128) then
  local value=emu.getState()['cpu.a'];pickupCalls[value]=(pickupCalls[value]or 0)+1
 end
end,emu.callbackType.exec,assert(L.ArHostNativePickup))
'''
 assert t.count(marker)==1;t=t.replace(marker,hook+marker)
 marker="  local x,y=wx(),r('Player_Y_Position')\n"
 observe='''  if r('Enemy_Flag',5)>0 and r('Enemy_ID',5)==46 and r('PowerUpType',5)==1 then
   if not seenItem then seenItem=true;questJump=nil;shot('released')end
   if r('Enemy_State',5)>=128 then mature=true end
  end
  if mature and(pickupCalls[6]or 0)>0 and r('ArLastPickup')==6 and r('ArR_053A')==68 then finish(r('NumberofLives')==startLives,'Natural flower reached original torch pickup');return end
  if age>=1600 then finish(false,'Natural flower controller bound');return end
'''
 assert t.count(marker)==1;t=t.replace(marker,marker+observe)
 return ref,t

def main():
 O.mkdir(exist_ok=True)
 ref,t=controller()
 rom=R/'build/shinobi-bbox-candidate-1101-v30/candidate.nes'
 prepare(O/'native2',rom,t,[Path(__file__),ref],expected=sha(rom),timeout=150,allow_interactive=True,scope='Cold Arthur controller-only firstflower: genuine headbump blockrelease, native itemmaturity, originalpickupA6/ArLastPickup and torch68. Readonly callbacks; no terrain/NPC/health/power/outcome writes. Atmost4PNGs/1600playframes. Doesnotclaim mushroom/star/1up/fullstage. Earlier native attempt stopped at x289: controller waited for exact y112 at input polling and never advanced.')

if __name__=='__main__':main()
