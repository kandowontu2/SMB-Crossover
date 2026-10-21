-- Explicit isolated projectile-render fixtures. B creates each cannon shot;
-- frozen unpacked SWF pixels independently check the committed OAM/CHR shape.
local ref=dofile(TEST_DIR..'fixtures/sophia-cannon-pixels.lua')
local banks=dofile(TEST_DIR..'fixtures/sophia-live-banks.lua')
local frame=0
local seen={}
local seenBanks={}
local slot
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/100),(frame-550)%100 end
local function picture()
 local state=ROM_NAME:find('mmc5')and emu.getState()or nil
 local cache={}
 local function chr(a)
  if cache[a]==nil then cache[a]=state and emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)end
  return cache[a]
 end
 local pixels={};local left,right,top,bottom=999,-999,999,-999
 for s=63,0,-1 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)+1
  local tile=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if x<184 and x+8>136 and y<120 and y+16>72 then
   local base=(tile&1)*4096+(tile&254)*16
   for dy=0,15 do for dx=0,7 do
    local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx
    local address=base+(row//8)*16+row%8
    local color=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
    if color>0 then
     local px,py=x+dx,y+dy
     pixels[py*256+px]=16+(a&3)*4+color
     left=math.min(left,px);right=math.max(right,px);top=math.min(top,py);bottom=math.max(bottom,py)
    end
   end end
  end
 end
 if right<left then return nil end
 local result={width=right-left+1,height=bottom-top+1,pixels={}}
 for y=top,bottom do for x=left,right do result.pixels[#result.pixels+1]=pixels[y*256+x]or 255 end end
 return result
end
local function rotated(source)
 local result={width=source.height,height=source.width,pixels={}}
 -- Flash right-facing rotation270 is one counterclockwise quarter turn.
 for y=0,result.height-1 do for x=0,result.width-1 do
  result.pixels[y*result.width+x+1]=source.pixels[x*source.width+(source.width-1-y)+1]
 end end
 return result
end
local function matches(actual,expected,mirror)
 if not actual or actual.width~=expected.width or actual.height~=expected.height then return false end
 for y=0,expected.height-1 do for x=0,expected.width-1 do
  local sx=mirror and expected.width-1-x or x
  if actual.pixels[y*expected.width+x+1]~=expected.pixels[y*expected.width+sx+1]then return false end
 end end
 return true
end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 local power=n//4
 w('PlayerStatus',power==0 and 0 or 1);w('InvOwnedLo',({1,0x81,0x91})[power+1],11);w('InvSelected',0,11)
 w('PlayerFacingDir',n%4%2==1 and 2 or 1);w('RgPreviousButtons',0);w('RgCooldown',0);w('RgShootPose',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 slot=nil;seen={};seenBanks={}
end
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,
  b=n>=0 and n<12 and t>=8 and t<12,up=n>=0 and n<12 and n%4>=2},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==12 then print('PASS Sophia Normal/Hyper/Crusher cannon source pixels across horizontal/upward and both facing cases');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selected Sophia');fixture(n)end
 if not slot then for i=0,9 do if r('RgShotType',i)==6 then slot=i;break end end end
 if slot then
  w('RgShotX',160,slot);w('RgShotPage',0,slot);w('RgShotY',96,slot);w('RgShotYHigh',1,slot)
  for _,name in ipairs({'RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi'})do w(name,0,slot)end
 end
 if t>=20 and t<80 then
  local bank=banks[(t//12)%#banks+1]
  w('PlayerChrBank',bank);w('ReloadCHRBank',1)
 end
 if t>=20 and t<80 then
  local actual=picture()
  for _,f in ipairs(n//4==0 and{1,2,3}or n//4==1 and{8}or{9,10,11,12})do
   if matches(actual,n%4>=2 and rotated(ref[f])or ref[f],n%4%2==1)then
    seen[f]=true
    if t%12>=3 then seenBanks[banks[(t//12)%#banks+1]]=true end
   end
  end
 end
 if t==85 then
  assert(slot,'B fired the cannon, case '..n)
  local any=false;for _,v in pairs(seen)do any=any or v end
  assert(any,'Committed cannon pixels match pinned source tier/direction, case '..n)
  for _,bank in ipairs(banks)do assert(seenBanks[bank],'Cannon prefix survives live CHR bank '..bank..', case '..n)end
  local f=assert(io.open(OUTPUT..ROM_NAME..'-sophia-cannon-'..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
