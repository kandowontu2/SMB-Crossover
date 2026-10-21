-- Explicit pickup/world fixture; compare actual DMA OAM and mapped CHR with
-- frozen source pixels through all eight selected suits, on both mappers.
local expected=dofile(TEST_DIR..'fixtures/bass-pickup-pixels.lua')
local frame,age,variant,item,matched=0,0,0,1,false
local references={3,4,5,6,7,8,13,1}
local checks=0
local spriteBanks,chrCache
local balanceSeen={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function chr(a)
 if chrCache[a]~=nil then return chrCache[a]end
 local value
 if ROM_NAME:find('mmc5')then
  local bank=spriteBanks['mapper.chrBanks'..math.floor(a/1024)]
  assert(bank and bank>=0 and bank<256,'Mapped sprite CHR bank stays inside the ROM')
  value=emu.read(bank*1024+a%1024,emu.memType.nesChrRom)
 else value=emu.read(a,emu.memType.nesPpuDebug)end
 chrCache[a]=value
 return value
end
local function pixels()
 spriteBanks=ROM_NAME:find('mmc5')and emu.getState()or nil
 chrCache={}
 local result={};for i=1,256 do result[i]=255 end
 for s=63,0,-1 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if y<112 and y+16>96 and x<176 and x+8>160 then
   local base=(t&1)*4096+(t&254)*16
   for dy=0,15 do for dx=0,7 do
    local px,py=x+dx,y+dy
    if px>=160 and px<176 and py>=96 and py<112 then
     local row=(a&128~=0)and(15-dy)or dy
     local col=(a&64~=0)and dx or(7-dx)
     local address=base+math.floor(row/8)*16+row%8
     local color=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
     if color>0 then result[(py-96)*16+px-160+1]=emu.read(16+(a&3)*4+color,emu.memType.nesPaletteRam)&63 end
    end
   end end
  end
 end
 return result
end
local function setup()
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9)
 w('InvSelected',variant,9);w('InvDirty',1)
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for x=0,15 do w('Block_Buffer_1',0x54,176+x)end
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Enemy_Flag',1);w('Enemy_ID',0x2e);w('Enemy_State',128);w('PowerUpType',1)
 w('Enemy_X_Position',160);w('Enemy_PageLoc',0);w('Enemy_Y_Position',88);w('Enemy_Y_HighPos',1)
 w('Enemy_SprAttrib',0);w('InvPickup',item);w('InvPickupOwner',9)
 matched=false;age=0;balanceSeen={}
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if age>=8 and not matched then
  local pic=pixels()
  local ref=references[item]
  if item==8 then ref=(r('FrameCounter')&4~=0)and 2 or 1 end
  for _,candidate in ipairs(item==8 and {1,2}or{ref})do
   local same=true
   for i,v in ipairs(expected[candidate])do if pic[i]~=v then same=false;break end end
   if same then
    if item==8 then balanceSeen[candidate]=true;matched=balanceSeen[1]and balanceSeen[2]
    else matched=true end
   end
  end
 end
 if age==25 then
  assert(matched,'Source pickup '..item..' matches hardware pixels in suit '..variant)
  if variant>0 then
   for y=0,15 do for x=0,15 do
    local tile=emu.read(0x2037+math.floor(y/8)*32+math.floor(x/8),emu.memType.nesPpuDebug)
    local address=tile*16+y%8
    local pixel=((emu.read(address,emu.memType.nesPpuDebug)>>(7-x%8))&1)+2*((emu.read(address+8,emu.memType.nesPpuDebug)>>(7-x%8))&1)
    assert(pixel==expected.hud[variant][y*16+x+1],'HUD shows the complete source icon: suit '..variant..' pixel '..x..','..y)
   end end
  end
  assert(r('EnemyMetasprite')==0,'Custom upgrade suppresses the native flower')
  assert(emu.read(0x19,emu.memType.nesPaletteRam)==0x16 and emu.read(0x1a,emu.memType.nesPaletteRam)==0x30 and emu.read(0x1b,emu.memType.nesPaletteRam)==0x27,'Mushroom/world palette remains correct')
  checks=checks+1
  if variant==0 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-pickup-'..item..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  item=item+1
  if item==9 then item=1;variant=variant+1 end
  if variant==8 then print('PASS '..checks..' source pickup/suit hardware OAM+CHR pixel comparisons, distinct icons, stable colors and native mushroom palette');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
