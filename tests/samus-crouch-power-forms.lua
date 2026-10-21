-- Synthetic flat-ground power fixtures; actual Down/B choose the poses.
local frame,index,age=0,0,0
local current
local cases={}
for power=0,2 do for dir=1,2 do cases[#cases+1]={power=power,dir=dir,seen={}}end end
local source=dofile(TEST_DIR..'samus-crouch-source.lua')
local suitless=dofile(TEST_DIR..'samus-suitless-crouch-source.lua')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
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
  local bodyBit=ROM_NAME:find('mmc5')and 0 or 1
  if y<240 and (t&1)==bodyBit and x<105 and x+8>46 then
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
local function expected(pose)
 local pic={}
 for y,row in ipairs((current.power==2 and suitless or source)[pose])do
  for x=1,#row do if row:sub(x,x)=='1'then
   local dx,dy=x-1-16,y-1-16
   if current.dir==2 then dx=15-dx end
   pic[dy*64+dx]=true
  end end
 end
 return pic
end
local function same(a,b)
 for k in pairs(a)do if not b[k]then return false end end
 for k in pairs(b)do if not a[k]then return false end end
 return true
end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100,start=frame==200,
  down=current and age>=5 and age<9,b=current and age>=20 and age<24},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if current then
  age=age+1
  if age>=10 then
   local actual=bodyPixels()
   for _,pose in ipairs({'CROUCH','CROUCHSHOOT'})do
    if same(actual,expected(pose))then current.seen[pose]=true end
   end
  end
  if age==30 and current.power==2 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-samus-suitless-crouch-'..current.dir..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
 end
 if not current or age==55 then
  if current then assert(current.seen.CROUCH and current.seen.CROUCHSHOOT,'Actual Samus DMA OAM/CHR must match power'..current.power..' direction'..current.dir..' crouch and shooting source silhouettes; crouch='..tostring(current.seen.CROUCH)..', shoot='..tostring(current.seen.CROUCHSHOOT)..', facing='..r('PlayerFacingDir'))end
  index=index+1;current=cases[index];age=0
  if not current then print('PASS Samus all3 power forms,2 facings and actual crouch/shoot OAM/CHR; fully powered suitless frames remain suitless');emu.stop(0);return end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
  w('PlayerStatus',current.power);w('InvOwnedLo',0,2);w('InvOwnedHi',0,2);w('InvSelected',0,2);w('AvSamusMode',0)
  w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',current.dir)
  w('SmCrouch',0);w('SmBall',0);w('SmShootPose',0);w('SmPreviousDirections',0);w('PlayerOutlinesOff',0);w('GuestPowerupActive',0);w('TimerControl',0)
 end
end,emu.eventType.endFrame)
