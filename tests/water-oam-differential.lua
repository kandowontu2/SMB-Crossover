-- Explicit OAM fixtures compare the two source Water40/41 pieces with the
-- generic signed metasprite contract, including palette overlay and flips.
-- No power-on progression or controller-only clear is claimed by this arena.
local frame,case,checks=0,0,0
local cases={}
for _,art in ipairs({38,39})do for _,dir in ipairs({1,2})do
 for _,x in ipairs({-10,-1,0,3,4,7,8,250,252,253,255,256,263})do
  for _,y in ipairs({-4,0,1,2,3,31,32,33,34,224,225,240,242,250,255,256})do
   cases[#cases+1]={art=art,dir=dir,x=x,y=y,offset=0,rotate=0,active=1}
  end
 end
 for _,offset in ipairs({4,240,248,252})do for _,rotation in ipairs({4,128,252})do
  for _,active in ipairs({0,1})do
   cases[#cases+1]={art=art,dir=dir,x=128,y=176,offset=offset,rotate=rotation,active=active}
  end
 end end
end end
local c
local interruptDepth=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local mmc5=ROM_NAME:find('mmc5')~=nil
local tileBase=mmc5 and 1 or 0xc0
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
local parts={
 [38]={[1]={{0,-1,0xc2,0x3a},{-4,-3,0xc0,0x38}},[2]={{-8,-1,0x82,0x3a},{-4,-3,0x80,0x38}}},
 [39]={[1]={{3,-4,0xc2,0x3e},{-5,-4,0xc2,0x3c}},[2]={{-11,-4,0x82,0x3e},{-3,-4,0x82,0x3c}}}}
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 then return end
 case=case+1;c=cases[case]
 if not c then print('PASS Water Shield exact source OAM: '..checks..' pieces with both frames/directions, edges, wrap, allocation limits and priority rotation');emu.stop(0);return end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 w('MmDeathFlag',0);w('CurrentOAMOffset',c.offset);w('GuestOamRotationActive',c.active)
 w('RgOamRotation',c.rotate);w('SsDrawFirst',0);if not mmc5 then w('GuestHudMixed',0)end
 for i=0,255 do emu.write(L.Sprite_Y_Position+i,i%4==0 and 248 or 77,emu.memType.nesDebug)end
 w('RgShotType',17,1);w('SsHidden',0,1);w('SsArt',c.art,1);w('RgShotDir',c.dir,1)
 w('ScreenLeft_X_Pos',254);w('ScreenLeft_PageLoc',1)
 local wx=(510+c.x)%65536
 w('RgShotX',wx,1);w('RgShotPage',math.floor(wx/256),1)
 w('RgShotY',c.y,1);w('RgShotYHigh',1+math.floor(c.y/256),1)
end,emu.callbackType.exec,L.SpecialDrawShots)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 or not c then return end
 local allocated=c.offset+8<256
 assert(r('CurrentOAMOffset')==(allocated and c.offset+8 or c.offset),'Exact logical OAM reservation '..case)
 if allocated then
  local first=(c.offset+(c.active~=0 and c.rotate or 0))%256
  for i,p in ipairs(parts[c.art][c.dir])do
   local o=(first+(i-1)*4)%256
   local x,y=c.x+p[1],c.y+p[2]
   if x<0 or x>255 or y<0 or y>255 then
    assert(r('Sprite_Y_Position',o)==248,'Clipped source piece '..case..'/'..i)
   else
    assert(r('Sprite_X_Position',o)==x and r('Sprite_Y_Position',o)==y,'Exact source position '..case..'/'..i)
    assert(r('Sprite_Tilenumber',o)==(p[4]|tileBase),'Exact source tile '..case..'/'..i)
    assert(r('Sprite_Attributes',o)==p[3],'Exact source flips and palette overlay '..case..'/'..i)
   end
   checks=checks+1
  end
 end
end,emu.callbackType.exec,L.SpecialDrawFinish)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
