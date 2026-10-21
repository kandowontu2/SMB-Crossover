-- Measured on the pinned original Rygar ROM with controller-only inputs:
-- native frames 304..313 (standing right) / 343..352 (crouched left).
local frame=0
local expected={{24,28,32,36,40,36,32,28,24,20},{22,26,30,34,38,34,30,26,22,18}}
local seen,previousAge={},-1
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function active()for i=0,9 do if r('RgShotType',i)==2 then return i end end end
local function phase()local n=math.floor((frame-550)/80);return n,(frame-550)%80 end
local function picture(name)local f=assert(io.open(OUTPUT..ROM_NAME..'-rygar-native-'..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({down=frame==80 or (n>=2 and n<=3),right=(frame>=100 and frame<120 and (frame-100)%20==0) or (n==5 and t>=5 and t<35),
  start=frame==200,b=n>=0 and n<6 and t==12,a=n==4 and t>=5 and t<30},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n,t=phase()
 if t==0 then
  if n==6 then print('PASS Rygar matches original disk extension/retraction offsets, windup, mirrored anchor, hand height and single chain tail');emu.stop(0);return end
  seen={};previousAge=-1
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
  for i=0,5 do w('Enemy_Flag',0,i) end
  for i=0,9 do w('RgShotType',0,i) end
  w('Player_X_Position',100);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',n%2==0 and 1 or 2);w('PlayerStatus',0)
  w('RgPreviousButtons',0);w('RgCooldown',0);w('RgShootPose',0);w('XgDiskReach',0);w('XgDiskReturning',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
 end
 local i=active()
 if n==0 and t>=12 and t<=29 then picture('sequence-'..(t-12)) end
 if i then
  local age=r('RgShotAge',i)
  if age<3 then assert(r('RgShotHits',i)==0,'No invisible windup hit') end
  if age>=3 and age~=previousAge then
   previousAge=age
   local center=r('Player_X_Position')+256*r('Player_PageLoc')+8
   local disk=r('RgShotX',i)+256*r('RgShotPage',i)
   local distance=math.abs(disk-center);seen[#seen+1]=distance
   local sequence=expected[(n%2)+1]
   -- Moving case faces right under its actual controller input.
   if n==5 then sequence=expected[1] end
   assert(distance==sequence[#seen],'Native disk sequence case '..n..' step '..#seen..': '..distance)
   assert(r('RgShotY',i)==r('Player_Y_Position')+((n==2 or n==3) and 15 or 8),'Disk follows the original stance / moving hand height')
   if n==0 then picture('frame-'..#seen) end
   if age>=5 and age<=10 then
    local tile=emu.read(0x20*8192+(L.XgRYGARWeapon8Right+1)%8192,emu.memType.nesPrgRom)
    local links=0
    for o=0,255,4 do if emu.read(o,emu.memType.nesSpriteRam)<240 and emu.read(o+1,emu.memType.nesSpriteRam)==tile then links=links+1 end end
    assert(links==1,'Actual Rygar OAM has the original single chain tail')
   end
  end
 end
 if t==65 then
  assert(#seen==10 and not active(),'Original unpowered flight has ten visible motion steps, case '..n..' / '..#seen)
  print('PASS Rygar original-return case '..n..': '..table.concat(seen,','))
 end
end,emu.eventType.endFrame)
