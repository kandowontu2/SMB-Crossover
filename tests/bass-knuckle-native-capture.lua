-- Initial mushroom/Knuckle inventory fixture only. All travel, enemy defeat
-- and the head bump use controller input on the native 1-1 map.
local frame,age,jump,spawn,airJump=0,0,nil,nil,nil
local fired,airFired=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
emu.addEventCallback(function()
 local live=frame>=550
 if live and x()>=334 and not jump then jump=age end
 if spawn and age>=spawn+70 and not airJump and r('Player_State')==0 then
  local liveKnuckle=false
  for i=0,9 do if r('RgShotType',i)==11 then liveKnuckle=true end end
  if not liveKnuckle then airJump=age end
 end
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140 or(live and not jump),start=frame==200,
  b=(live and x()<304 and age%24<6)or(airJump and age-airJump>=2 and age-airJump<8),
  a=(jump and age-jump<24)or(airJump and age-airJump<16)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  w('PlayerStatus',1);w('InvOwnedLo',9,9);w('InvOwnedHi',0,9);w('InvSelected',3,9);w('InvDirty',1)
  return
 end
 age=age+1
 for i=0,9 do if r('RgShotType',i)==11 then
  fired=true
  if airJump and r('Player_State')~=0 and r('RgShotAge',i)<3 then airFired=true end
 end end
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
  if not spawn then spawn=age end
  assert(r('InvPickup',i)>0 and r('InvPickup',i)<252,'Native head bump reveals a distinct weapon upgrade')
 end end
 assert(r('PlayerStatus')==1 and r('InvOwnedLo',9)==9 and r('InvOwnedHi',9)==0,'Native first-block head bump does not automatically collect its upgrade: age '..age..' x '..x()..' status '..r('PlayerStatus')..' own '..r('InvOwnedLo',9)..'/'..r('InvOwnedHi',9)..' spawn '..tostring(spawn))
 assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Knuckle firing preserves the sky palette during native travel')
 local f=assert(io.open(OUTPUT..ROM_NAME..'-knuckle-head-'..string.format('%04d',age)..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 if airJump and age>=airJump+80 then
  assert(fired and jump and airFired,'Controller ground/air Knuckle fire, travel and head contact were all exercised')
  print('PASS native 1-1 Knuckle firing and first upgrade head bump: '..age..' captured frames, item remains uncollected');emu.stop(0)
 end
 assert(age<700,'Native first upgrade block is reached and head-bumped, then air Knuckle is fired')
end,emu.eventType.endFrame)
