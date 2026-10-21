-- Explicit isolated projectile-render fixtures. B creates each cannon shot;
-- frozen unpacked SWF pixels independently check the committed OAM/CHR shape.
local ref=dofile(TEST_DIR..'fixtures/sophia-cannon-pixels.lua')
local impacts=dofile(TEST_DIR..'fixtures/sophia-impact-pixels.lua')
local banks=dofile(TEST_DIR..'fixtures/sophia-live-banks.lua')
local frame=0
local seen={}
local cases={}
for turn=0,3 do for _,mirror in ipairs({false,true})do for phase=0,1 do cases[#cases+1]={turn=turn,mirror=mirror,phase=phase}end end end
for impact=1,5 do cases[#cases+1]={impact=impact}end
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
 if expected.width==0 then return actual==nil end
 if not actual or actual.width~=expected.width or actual.height~=expected.height then return false end
 for y=0,expected.height-1 do for x=0,expected.width-1 do
  local sx=mirror and expected.width-1-x or x
  if actual.pixels[y*expected.width+x+1]~=expected.pixels[y*expected.width+sx+1]then return false end
 end end
 return true
end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',1);w('InvOwnedLo',0x83,11);w('InvSelected',1,11);w('InvAmmo',60,177);w('InvPrevious',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 slot=nil;seenBanks={}
end
emu.addMemoryCallback(function()
 local n,t=phase();local c=cases[n+1]
 if not c or not slot or r('CurrentBank')%128~=37 or r('RgSlot')~=slot then return end
 w('RgShotType',44,slot);w('RgShotX',160,slot);w('RgShotPage',0,slot);w('RgShotY',96,slot);w('RgShotYHigh',1,slot)
 w('SsMode',1,slot)
 w('RgShotImpact',c.impact and 12-c.impact*2 or 0,slot)
 w('RgShotAge',c.phase==1 and 2 or 0,slot)
 w('XgShotAim',c.impact and 0 or c.turn*8+(c.mirror and 64 or 0),slot)
end,emu.callbackType.exec,assert(L.ExpandedWeaponPointer))
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=n>=0 and n<#cases and t>=8 and t<12},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase();local c=cases[n+1]
 if not c then print('PASS Sophia source missile flame/unlit rotations and all five impact frames across live CHR banks');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selected Sophia');fixture()end
 if not slot then for i=0,9 do if r('RgShotType',i)==44 then slot=i;break end end end
 if slot then
  for i=0,9 do if i~=slot then w('RgShotType',0,i)end end
  w('RgShotX',160,slot);w('RgShotPage',0,slot);w('RgShotY',96,slot);w('RgShotYHigh',1,slot)
  for _,name in ipairs({'RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi'})do w(name,0,slot)end
  w('RgShotImpact',0,slot)
 end
 if t>=20 and t<80 then
  local bank=banks[(t//12)%#banks+1];w('PlayerChrBank',bank);w('ReloadCHRBank',1)
  local expected=c.impact and impacts[c.impact]or ref[c.phase==1 and 4 or 5]
  if not c.impact then for turn=1,c.turn do expected=rotated(expected)end end
  if matches(picture(),expected,c.mirror)and t%12>=3 then seenBanks[bank]=true end
 end
 if t==85 then
  assert(slot,'Select fired source missile, case '..n)
  for _,bank in ipairs(banks)do assert(seenBanks[bank],'Missile/impact source pixels survive live CHR bank '..bank..', case '..n)end
 end
end,emu.eventType.endFrame)
