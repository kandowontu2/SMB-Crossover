-- Explicit isolated art fixtures. Actual Select creates each projectile; its
-- completed DMA OAM/CHR pixels must match the exact pinned source flame phase.
-- RyuProjectile.setDirection never changes scaleX, even for a leftward throw.
local ref=dofile(TEST_DIR..'fixtures/ryu-fire-projectile-pixels.lua')
local frame=0
local firstCase=RYU_FIRE_FIRST or 0
local draw,dma,slot
local seen={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return (frame-550)//120+firstCase,(frame-550)%120 end
local function picture()
 local state=ROM_NAME:find('mmc5')and emu.getState()or nil
 local cache={}
 local function chr(a)
  if cache[a]==nil then cache[a]=state and emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)end
  return cache[a]
 end
 local pixels={};local x0,x1,y0,y1=999,-999,999,-999
 for s=0,63 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)+1
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if x>=110 and x<210 and y>=40 and y<150 then
   local base=(t&1)*4096+(t&254)*16
   for dy=0,15 do for dx=0,7 do
    local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx
    local address=base+(row//8)*16+row%8
    local color=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
    if color~=0 then
     local px,py=x+dx,y+dy;pixels[py*256+px]=true
     x0=math.min(x0,px);x1=math.max(x1,px);y0=math.min(y0,py);y1=math.max(y1,py)
    end
   end end
  end
 end
 local rows={}
 for y=y0,y1 do local row={};for x=x0,x1 do row[#row+1]=pixels[y*256+x]and'1'or'0'end;rows[#rows+1]=table.concat(row)end
 return table.concat(rows,'\n')
end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',1);w('PlayerFacingDir',n%2+1);w('InvOwnedLo',0x15,10);w('InvSelected',n<2 and 2 or 4,10);w('InvAmmo',50,160)
 w('RgAttack',0);w('RgCooldown',0);w('RgPreviousButtons',0);w('AvSlash',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 draw=nil;dma=nil;slot=nil;seen={}
end
emu.addMemoryCallback(function()draw=nil end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 local n,t=phase()
 if n>=0 and n<4 and t>=20 and t<100 and r('SelectedCharacter')==10 and slot and r('R4')>=110 and r('R4')<210 and r('R6')>=40 and r('R6')<150 then
  local kind=r('RgShotType',slot)
  if kind==39 or kind==40 then draw={case=n,index=(r('RgShotAge',slot)//4)%4+(kind==39 and 4 or 0)+1}end
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()dma=draw end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({down=frame==80,right=frame>=100 and frame<180 and(frame-100)%20==0,start=frame==240,
  select=n>=0 and n<4 and t>=8 and t<13},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==4 then print('PASS Ryu '..(firstCase==2 and 'dragon' or 'fire-wheel/dragon')..' source flame pixels and launch velocities, both directions, completed DMA OAM/CHR');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==10,'Real menu selected Ryu');fixture(n)end
 if not slot then for i=0,9 do if r('RgShotType',i)==(n<2 and 39 or 40)then
  slot=i
  local function velocity(axis)
   local v=r('RgShotV'..axis..'Hi',i)*256+r('RgShotV'..axis..'Lo',i)
   return v>=32768 and v-65536 or v
  end
  -- Source600 * .75 Flash pixels/s /120 =3.75 NES pixels/update.
  assert(velocity('X')==(n%2==0 and 960 or -960),'Source horizontal flame launch velocity, case '..n)
  assert(velocity('Y')==(n<2 and -960 or 960),'Source wheel-up/dragon-down launch velocity, case '..n)
  local shotAge=r('RgShotAge',i)
  local px=r('Player_PageLoc')*256+r('Player_X_Position')
  local actualX=(r('RgShotPage',i)*256+r('RgShotX',i))*256+r('RgShotFracX',i)
  local actualY=r('RgShotY',i)*256+r('RgShotFracY',i)
  local expectedX=(px+8+(n%2==0 and 15 or -15))*256+velocity('X')*shotAge
  local expectedY=(r('Player_Y_Position')+11)*256+velocity('Y')*shotAge
  assert(actualX==expectedX and actualY==expectedY,string.format('Source standing flame muzzle, case %d: %g,%g expected %g,%g',n,actualX/256,actualY/256,expectedX/256,expectedY/256))
  break
 end end end
 if slot then
  assert(r('RgShotDir',slot)==n%2+1,'Art selection preserves actual flame motion direction, case '..n)
  w('RgShotX',160,slot);w('RgShotPage',0,slot);w('RgShotY',96,slot);w('RgShotYHigh',1,slot)
  for _,name in ipairs({'RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi'})do w(name,0,slot)end
 end
 if t>=25 and t<95 and dma and dma.case==n then
  local expected=table.concat(ref[dma.index],'\n')
  assert(picture()==expected,'Exact source flame phase '..dma.index..' for launch direction '..(n%2+1)..' at '..frame)
  seen[dma.index]=true
 end
 if t==105 then
  assert(slot,'Actual Select launched source projectile, case '..n)
  local first=n<2 and 5 or 1
  for i=first,first+3 do assert(seen[i],'Every source phase checked for case '..n..': '..i)end
 end
end,emu.eventType.endFrame)
