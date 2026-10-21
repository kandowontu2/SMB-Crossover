-- Explicit flat-ground/ceiling and mature-pickup fixtures. Every transition
-- and shot is driven by actual controller input; these are not level clears.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local source=dofile(TEST_DIR..'samus-crouch-source.lua')
local pixelChecks={}
local function bodyPixels()
 local state=ROM_NAME:find('mmc5')and emu.getState()or nil
 local cache={}
 local function chr(a)
  if cache[a]==nil then cache[a]=state and emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)end
  return cache[a]
 end
 local pic={}
 for s=63,0,-1 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  local base=(t&1)*4096+(t&254)*16
  if y<240 and x<105 and x+8>46 then
   for dy=0,15 do for dx=0,7 do
    local px,py=x+dx-64,y+dy-176
    if px>=-16 and px<22 and py>=-16 and py<48 then
     local row=a&128~=0 and 15-dy or dy
     local col=a&64~=0 and dx or 7-dx
     local address=base+(row//8)*16+row%8
     local color=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
     if color~=0 then pic[py*64+px]=true end
    end
   end end
  end
 end
 return pic
end
local function expected(pose,dir)
 local pic={}
 for y,row in ipairs(source[pose])do for x=1,#row do if row:sub(x,x)=='1'then
  local dx,dy=x-1-16,y-1-16
  if dir==2 then dx=15-dx end
  pic[dy*64+dx]=true
 end end end
 return pic
end
local function same(a,b)
 for k in pairs(a)do if not b[k]then return false end end
 for k in pairs(b)do if not a[k]then return false end end
 return true
end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 w('PlayerStatus',0);w('InvOwnedLo',1,2);w('InvOwnedHi',0,2);w('InvSelected',0,2)
 w('SmBall',0);w('SmCrouch',0);w('SmShootPose',0);w('SmPreviousDirections',0)
 w('AvSamusMode',0);w('PlayerOutlinesOff',0)
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or(frame>=630 and frame<635),start=frame==200,
  down=frame==560 or frame==600 or frame==665 or frame==675 or frame==760 or frame==800,
  up=frame==610 or frame==700,b=frame==580 or frame==720,
  a=frame==740 or frame==780},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then fixture()end
 if frame>550 and frame<650 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if frame>=565 and frame<=588 then
  assert(r('SmCrouch')==1 and r('SmBall')==0,'First Down crouches before Morph Ball is owned')
  -- Source frames31/32 have nominal15.5NES height; the native integer
  -- projection keeps foot32 and uses top17 (existing profile14).
  assert(r('Player_BoundBoxCtrl')==14,'Crouch uses the source-backed short body profile')
  assert((r('BoundingBox_UL_Corner',1)-r('Player_Rel_YPos'))%256==17,'Crouch body top is the integer projection17')
  assert((r('BoundingBox_UL_Corner',3)-r('Player_Rel_YPos'))%256==32,'Crouch keeps the native foot32')
  local a=bodyPixels()
  for _,pose in ipairs({'CROUCH','CROUCHSHOOT'})do if same(a,expected(pose,1))then pixelChecks[pose]=true end end
 end
 if frame==582 then
  assert(r('SmPose')==32 and r('SmShotY',2)==195,'Crouched beam uses source pose and19-pixel muzzle')
 end
 if frame==605 then assert(r('SmCrouch')==1 and r('SmBall')==0,'Second Down cannot morph before the upgrade')end
 if frame==615 then assert(r('SmCrouch')==0,'Up exits crouch')end
 if frame==640 then assert(r('Player_X_Position')>64,'Walking resumes after standing')end
 if frame==650 then
  fixture();w('PlayerStatus',1)
  -- The real pickup collision grants Morph Ball and missiles, not a direct
  -- ownership patch. They are placed one at a time in the native hit box.
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('InvPickupOwner',2,5);w('InvPickup',1,5);w('PowerUpType',1,5)
 end
 if frame==670 then assert(r('InvOwnedLo',2)&2~=0 and r('SmCrouch')==1 and r('SmBall')==0,'Owned Morph still requires crouch then a second Down edge')end
 if frame==680 then
  assert(r('SmBall')==1 and r('SmCrouch')==0,'Second Down enters persistent Morph Ball')
  for x=64,80,16 do w('Block_Buffer_1',0x61,cell(x,176))end
 end
 if frame==705 then assert(r('SmBall')==1,'A low ceiling prevents expansion into solid terrain')end
 if frame==710 then for x=64,80,16 do w('Block_Buffer_1',0,cell(x,176))end end
 if frame==745 then assert(r('SmBall')==0 and r('MmVY',2)<128,'A exits clear Morph Ball without launching a jump')end
 if frame==755 then fixture()end
 if frame==765 then assert(r('SmCrouch')==1,'Another first Down crouches')end
 if frame==785 then assert(r('SmCrouch')==0 and r('Player_State')~=0,'A jumps from crouch')end
 if frame==820 then
  assert(pixelChecks.CROUCH and pixelChecks.CROUCHSHOOT,'Actual DMAOAM/CHR matches independent2.02 crouch and shooting silhouettes')
  print('PASS Samus2.02 crouch, source pixels, muzzle, upgrade-gated two-Down Morph, clearance and jump/stand exits');emu.stop(0)
 end
end,emu.eventType.endFrame)
