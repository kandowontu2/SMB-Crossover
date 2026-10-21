local frame=0
local draws=0
local all,seen={},{}
local body={}
local patterns={}
local phase=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200,down=frame>=560,b=frame==570},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 -- Contra's NMI driver switches physical banks without changing the
 -- interrupted CurrentBank byte. The same CPU address can execute there.
 if r('CurrentBank')%128~=4 or r('CurrentBankC')%128~=19 then return end
 if not((phase==0 and frame>=590 and frame<=680)or(phase==1 and frame>=700 and frame<=790))then return end
 draws=draws+1
 local row=201
 local first={}
 local function key(offset)
  return r('Sprite_Tilenumber',offset)..':'..r('Sprite_Attributes',offset)..':'..r('Sprite_X_Position',offset)..':'..(r('Sprite_Y_Position',offset)+1)
 end
 for offset=0,255,4 do
  local y=r('Sprite_Y_Position',offset)+1
  if y<=row and y+16>row then
   local id=key(offset)
   all[id]=true
   if #first<8 then first[#first+1]=id;seen[id]=true end
  end
 end
 patterns[table.concat(first,',')]=true
 local pointer=r('SmPosePtr')+256*r('SmPosePtr',1)
 local size=emu.read(pointer,emu.memType.nesDebug)
 for logical=r('RgOamPlayerStart'),r('RgOamPlayerStart')+size-1,4 do
  local offset=(logical+r('RgOamRotation'))%256
  local y=r('Sprite_Y_Position',offset)+1
  if y<=row and y+16>row then local id=key(offset);body[id]=(body[id] or 0)+1 end
 end
end,emu.callbackType.exec,assert(L.RosterOamReady,'OAM completion label'))
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then w('PlayerStatus',2) end
 if frame==580 then
  -- Ten stationary spread bullets keep the same body and crowded row alive
  -- long enough to measure fairness without one-frame animation transients.
  for i=0,9 do
   w('RgShotType',3,i);w('RgShotX',140+6*i,i);w('RgShotPage',0,i)
   w('RgShotY',198,i);w('RgShotYHigh',1,i);w('RgShotImpact',0,i);w('RgShotAge',0,i)
   w('RgShotVXHi',0,i);w('RgShotVXLo',0,i);w('RgShotVYHi',0,i);w('RgShotVYLo',0,i)
  end
  w('RgShootPose',0)            -- Pin the intended persistent resting pose.
 end
 if phase==1 then w('RgShootPose',12)end -- Separate persistent shooting pose.
 if frame==605 or frame==606 or frame==715 or frame==716 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-crouch-overload-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if frame==681 or frame==791 then
  local total,visible,orders=0,0,0
  for _ in pairs(all) do total=total+1 end
  for _ in pairs(seen) do visible=visible+1 end
  for _ in pairs(patterns) do orders=orders+1 end
  assert(draws>30 and total>8 and orders>8,'Replay overloads a crouched Bill scanline and changes hardware priority: '..draws..' draws, '..total..' parts, '..orders..' orders')
  -- Every part of the persistent crouching pose must win a hardware slot.
  local missing=0
  for key in pairs(body) do if not seen[key] then missing=missing+1 end end
  assert(missing==0,'Every crouching body part shares scanline visibility')
  print('PASS crowded crouching Bill '..(phase==0 and 'resting' or 'shooting')..' row rotates visible sprite parts: '..orders..' priority orders, '..visible..'/'..total..' parts seen')
  if phase==0 then
   phase=1;draws=0;all={};seen={};body={};patterns={}
  else emu.stop(0)end
 end
end,emu.eventType.endFrame)
