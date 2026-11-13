-- Separate stock route: all three authored 1-1 ordinary blocks, then 1-2/160
-- and 1-2/1104. Existing native manual girders; no game-memory writes.
local EARLY_APPROACH_X=1720
local EARLY_CARRY_Y=80
local early={stage='approach',start=0,heads={},motion={}}
stockFifth.early=early
local function earlyTo(name)early.stage=name;early.start=stockFifth.main;routePhase='early-high-'..name;routeAge=0;early.last=state()end
local function earlyControl(x,y,ground,item)
 if #pickups==2 and r('LevelNumber')==0 and x>=1680 and not item then
  early.entered=early.entered or stockFifth.main;assert(stockFifth.main-early.entered<700,'Authored high-question total Main bound')
  local age=stockFifth.main-early.start
  if early.stage=='low-block'or early.stage=='head'then
   if stockFifth.main%4==0 then
    early.motion[#early.motion+1]={main=stockFifth.main,x=x,y=y,ground=ground,native_dy=r('Player_Y_Speed'),pad=r('SavedJoypadBits'),flags=kr(0x62),held=kr(0x1b),pressed=kr(0x21),air=kr(0x66)}
    if #early.motion>32 then table.remove(early.motion,1)end
   end
  end
  if ground then local clear=fifthClearEnemy(x,y);if clear then return true,clear end end
  if early.stage=='approach'then
   if not ground then return true,0 end
   if x<EARLY_APPROACH_X then return true,1 elseif x>EARLY_APPROACH_X then return true,2 end
   earlyTo('request');return true,40
  elseif early.stage=='request'then
   for i=0,5 do local a=actor(i)
    if a.flag==1 and a.id==37 and a.state==65 and math.abs(a.x-(x-8))<=1 then early.slot=i;earlyTo('ride');return true,0 end
   end
   assert(age<40,'Existing native girder for authored high 1-1 question');return true,age<3 and 40 or 0
  elseif early.stage=='ride'then
   -- The authored lower coin block at1744/Y144 is directly below the
   -- high question. Rise in the open adjacent column, then land on that
   -- ordinary block before the fresh jump; do not ride through it.
   if y<=EARLY_CARRY_Y then
    early.geometry={};for column=1696,1776,16 do local row={x=column,tiles={}};for yy=64,144,16 do row.tiles[#row.tiles+1]={yy,tile(column,yy)}end;early.geometry[#early.geometry+1]=row end
    earlyTo('low-block')
   end
   assert(age<180,'Native carry to high-question head approach');return true,0
  elseif early.stage=='low-block'then
   if x<1737 then return true,1|(age<36 and 128 or 0)elseif x>1737 then return true,2 end
   if ground and y==112 then earlyTo('release')end
   assert(age<120,'Ordinary landing on authored lower coin block');return true,0
  elseif early.stage=='release'then
   if age>=3 then earlyTo('head')end;return true,0
  end
  assert(age<120,'Fresh original jump reveals authored high question')
  return true,age<9 and 128 or 0
 end
 if #pickups==3 and r('LevelNumber')==1 and r('AreaType')==2 and x<256 and not item then
  if kr(0x65)&128==0 and kr(0xbd)>0 then
   if not ground then return true,0 end
   return true,routeAge%8<2 and 68 or 0
  end
  if x<152 then if ground then local clear=fifthClearEnemy(x,y);if clear then return true,clear end end;return true,1 end
  if ground and epoch-lastPulse>30 then lastPulse=epoch;early.cave_until=epoch+6 end
  return true,early.cave_until and epoch<early.cave_until and 128 or 0
 end
 return false,0
end
emu.addMemoryCallback(function()
 if #pickups~=2 or r('LevelNumber')~=0 or wx()<1696 or wx()>1776 then return end
 local q=emu.convertAddress(L.NativeRarePlayerHeadCollisionCore)
 if not q or q.memType~=emu.memType.nesPrgRom or q.address~=HEAD_OFFSET then return end
 local c=emu.getState()
 early.heads[#early.heads+1]={s=state(),tile=c['cpu.a'],native_pad=r('SavedJoypadBits'),native_dy=r('Player_Y_Speed'),source_held=kr(0x1b),source_pressed=kr(0x21)}
 if #early.heads>12 then table.remove(early.heads,1)end
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
