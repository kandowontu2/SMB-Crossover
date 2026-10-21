-- Independent source pixels against committed OAM/CHR for all six private
-- enemy-explosion frames, including intentional blank9, in every live body bank.
local ref=dofile(TEST_DIR..'fixtures/sophia-enemy-pixels.lua')
local banks=dofile(TEST_DIR..'fixtures/sophia-live-banks.lua')
local frame=0
local depth=0
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced interrupt guards')end,emu.callbackType.exec,pc)end
local seen={}
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
 for i=0,5 do w('Enemy_Flag',0,i);w('SophiaEffectAge',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('InvSelected',0,11);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
 w('SophiaEffectX',160);w('SophiaEffectPage',0);w('SophiaEffectY',96);w('SophiaEffectYHigh',1)
 seen={}
end
emu.addMemoryCallback(function()
 local n,t=phase()
 if n<0 or n>=6 or depth~=0 or r('CurrentBank')%128~=61 then return end
 w('SophiaEffectAge',n*2+1)
end,emu.callbackType.exec,assert(L.RemainingDraw))
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==6 then print('PASS Sophia enemy explosion source frames8..13 incl blank9 across every live CHR body bank');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selected Sophia');fixture()end
 if t>=10 and t<80 then
  local bank=banks[(t//12)%#banks+1];w('PlayerChrBank',bank);w('ReloadCHRBank',1)
  if matches(picture(),ref[n+1],false)and t%12>=4 then seen[bank]=true end
 end
 if t==85 then for _,bank in ipairs(banks)do assert(seen[bank],'Source enemy-death pixels survive bank '..bank..', phase '..n)end end
end,emu.eventType.endFrame)
