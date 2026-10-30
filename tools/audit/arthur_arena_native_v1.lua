-- Native controller arena proof. No writes to emulated RAM/registers/state.
local frame=0
local steps=0
local nmis=0
local originalWeapons={}
local visibleWeapons={}
local calls={}
local minSingle=255
local minDouble=255
local maxJumpCount=0
local minX=255
local maxX=0
local hardwareBody=false
local firstUpdates=nil
local csv=assert(io.open(OUTPUT..'frames.csv','w'))
csv:write('frame,pad,mode,x,y,jumps,weapon,pose,parts,steps,nmi\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addMemoryCallback(function()steps=steps+1 end,emu.callbackType.exec,assert(L.ArStep))
emu.addMemoryCallback(function()nmis=nmis+1 end,emu.callbackType.exec,assert(L.Nmi))
for _,name in ipairs({'ArNativeLance','ArNativeDagger','ArNativeTorch','ArNativeAxe','ArNativeCross'})do
 emu.addMemoryCallback(function()calls[name]=(calls[name]or 0)+1 end,emu.callbackType.exec,assert(L[name]))
end
emu.addEventCallback(function()
 local b={right=frame>=50 and frame<110 or frame>=440 and frame<460,
  down=frame>=420 and frame<450,
  a=frame>=120 and frame<126 or frame>=220 and frame<226 or frame>=238 and frame<244 or frame>=250 and frame<256,
  b=frame>=360 and frame<366 or frame>=400 and frame<406}
 for _,at in ipairs({500,580,660,740,820})do
  if frame>=at and frame<at+4 then b.select=true end
  if frame>=at+10 and frame<at+18 then b.b=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>40 then
  local x,y=r('ArR_05AF'),r('ArR_0599')
  minX=math.min(minX,x);maxX=math.max(maxX,x);maxJumpCount=math.max(maxJumpCount,r('ArJumpCount'))
  if frame>=120 and frame<200 then minSingle=math.min(minSingle,y)end
  if frame>=220 and frame<320 then minDouble=math.min(minDouble,y)end
  assert(r('ArDead')==0,'Technical arena has no death or immunity fixture')
  originalWeapons[r('ArR_053A')]=true
  for slot=17,19 do if r('ArR_04F0',slot)~=0 then visibleWeapons[r('ArR_0631',slot)]=true end end
  for slot=0,63 do
   local at=slot*4;local y0=emu.read(at,emu.memType.nesSpriteRam);local tile=emu.read(at+1,emu.memType.nesSpriteRam)
   if y0<240 and tile==17 then hardwareBody=true end
  end
  csv:write(table.concat({frame,r('ArArenaPad'),r('ArMode'),x,y,r('ArJumpCount'),r('ArR_053A'),r('ArR_0522'),r('ArArenaPartCount'),steps,nmis},',')..'\n')
 end
 for _,target in ipairs({142,250,380,448,690,770})do if frame==target then
  local f=assert(io.open(OUTPUT..string.format('f%04d.png',frame),'wb'));f:write(emu.takeScreenshot());f:close()
 end end
 if frame==1000 then
  csv:close()
  assert(minSingle==152,'Native single jump apex must remain32 source pixels')
  assert(minDouble==120,'Authored second edge must produce two native32px rises')
  assert(maxJumpCount==2,'Third fresh press must not grant a third jump')
  assert(maxX-minX>=60,'Actual native Right input must move at least60px')
  assert(steps>=300 and steps<=340,'Original three-NMI cadence must be retained')
  assert(nmis>950 and hardwareBody,'Actual NMI and displayed original head tile required')
  for _,weapon in ipairs({0x40,0x42,0x44,0x36,0x4f})do assert(originalWeapons[weapon],'All native inventory kinds reached by controller fixtures')end
  for _,kind in ipairs({0x23,0x24,0x25,0x26,0x27})do assert(visibleWeapons[kind],'All native projectile kinds allocated')end
  for _,name in ipairs({'ArNativeLance','ArNativeDagger','ArNativeTorch','ArNativeAxe','ArNativeCross'})do assert((calls[name]or 0)>0,name..' actual handler execution')end
  local f=assert(io.open(OUTPUT..'receipt.json','w'))
  f:write('{"status":"PASS_NATIVE_PRIVATE_LEAF_CONTROLLER_ARENA","frames":1000,"single_jump_pixels":'..(184-minSingle)..',"double_jump_pixels":'..(184-minDouble)..',"max_jump_count":'..maxJumpCount..',"steps":'..steps..',"NMIs":'..nmis..',"actual_OAM_body":true,"all_five_weapon_handlers":true,"memory_writes":false,"limits":"Private flat arena and controller-selected pickup fixtures; no earned progression, native tile bridge, host integration or campaign admission."}\n');f:close()
  print('PASS Arthur original-kernel private controller arena1000; single32/double64; all five real handlers; no host admission');emu.stop(0)
 end
end,emu.eventType.endFrame)
