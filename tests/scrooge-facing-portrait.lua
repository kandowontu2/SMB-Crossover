-- Real menu navigation; flat ground isolates native left/right walking pixels.
local native=dofile(TEST_DIR..'scrooge-native-silhouettes.lua')
local crouch=dofile(TEST_DIR..'scrooge-native-crouch.lua')
local frame=0
local seen={right={},left={}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function shot(n)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-'..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function portrait()
 -- Actual background nametable/CHR, including the bottom row of the portrait.
 local rows=native.stand
 local left=(32-#rows[1])//2
 local top=40-#rows
 for y=0,39 do for x=0,31 do
  local t=emu.read(0x2000+(12+y//8)*32+11+x//8,emu.memType.nesPpuDebug)
  local a=t*16+y%8
  local color=((emu.read(a,emu.memType.nesPpuDebug)>>(7-x%8))&1)+2*((emu.read(a+8,emu.memType.nesPpuDebug)>>(7-x%8))&1)
  local expected=y>=top and x>=left and x<left+#rows[1] and rows[y-top+1]:sub(x-left+1,x-left+1)=='1'
  assert((color~=0)==not not expected,'Full native Scrooge portrait pixel at '..x..','..y)
 end end
end
local function silhouette()
 local state=ROM_NAME:find('mmc5') and emu.getState() or nil
 local function chr(a)
  if state then return emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)end
  return emu.read(a,emu.memType.nesPpuDebug)
 end
 local px,py=r('Player_Rel_XPos'),r('Player_Y_Position')
 local pixels={}
 local x0,x1,y0,y1=256,0,240,0
 for s=0,63 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)+1
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if x>=px-32 and x<px+32 and y>=py-8 and y<py+40 then
   local base=(t&1)*4096+(t&254)*16
   for dy=0,15 do for dx=0,7 do
    local row=a&128~=0 and 15-dy or dy
    local col=a&64~=0 and dx or 7-dx
    local address=base+(row//8)*16+row%8
    local c=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
    if c~=0 then
     pixels[(y+dy)*256+x+dx]=true
     x0=math.min(x0,x+dx);x1=math.max(x1,x+dx);y0=math.min(y0,y+dy);y1=math.max(y1,y+dy)
    end
   end end
  end
 end
 local rows={}
 for y=y0,y1 do
  local row={};for x=x0,x1 do row[#row+1]=pixels[y*256+x] and '1' or '0'end
  rows[#rows+1]=table.concat(row)
 end
 return table.concat(rows,'\n')
end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('Player_X_Position',100);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==220,down=frame==80 or(frame>=800 and frame<830)or(frame>=840 and frame<870),right=frame==100 or frame==120 or(frame>=600 and frame<645),
  left=frame>=700 and frame<745},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==215 then
  assert(r('SelectedCharacter')==12,'Menu selects Scrooge');portrait();shot('portrait-fixed')
 end
 if frame==590 or frame==690 then fixture()end
 local side=frame>=610 and frame<=640 and 'right' or frame>=710 and frame<=740 and 'left' or nil
 if side then
  assert(r('PlayerFacingDir')==(side=='right' and 1 or 2),'Controller facing agrees with movement')
  local pic=silhouette();local match
  for name,rows in pairs(native)do
   if name~='stand' then
    local expected={}
    for i,row in ipairs(rows)do expected[i]=side=='left' and row:reverse()or row end
    if pic==table.concat(expected,'\n')then match=name;break end
   end
  end
  assert(match,'DMA OAM/CHR Scrooge '..side..' walk must match a complete native DuckTales pose, frame '..frame)
  seen[side][match]=true
  if frame==630 or frame==730 then shot('walk-'..side..'-fixed')end
 end
 if frame==780 then
  for _,side in ipairs({'right','left'})do for _,pose in ipairs({'walk1','walk2','walk3'})do
   assert(seen[side][pose],'All three native '..side..' walk poses rendered')
  end end
  print('PASS full Scrooge menu silhouette and all three native walking poses facing both controller directions, actual PPU/OAM/CHR pixels')
 end
 if frame==790 or frame==830 then fixture();w('PlayerFacingDir',frame==790 and 1 or 2)end
 if(frame>=815 and frame<=825)or(frame>=855 and frame<=865)then
  local expected={}
  for i,row in ipairs(crouch)do expected[i]=frame<830 and row or row:reverse()end
  assert(r('RgCrouch')~=0,'Real Down input activates crouch')
  assert(silhouette()==table.concat(expected,'\n'),'DMA OAM/CHR crouch must match the independently captured native20px silhouette')
 end
 if frame==880 then print('PASS Scrooge native crouch art in both directions, actual completed-DMA OAM and CHR pixels');emu.stop(0)end
end,emu.eventType.endFrame)
