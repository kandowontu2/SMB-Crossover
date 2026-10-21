-- Explicit crowded-row fixture: four live buster shots, six Koopas and the
-- player compete for native eight-sprite scanline visibility.
local frame,draws=0,0
local seen,all,orders={},{},{}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function key(o) return r('Sprite_Tilenumber',o)..':'..r('Sprite_Attributes',o)..':'..r('Sprite_X_Position',o)..':'..r('Sprite_Y_Position',o) end
emu.addEventCallback(function() emu.setInput({right=frame==80,start=frame==120},0) end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if r('CurrentBank')%128~=4 or frame<590 or frame>680 then return end
 for i=0,3 do
  w('MmBulletType',i==3 and 3 or 1,i);w('MmBulletX',104+24*i,i);w('MmBulletPage',0,i)
  w('MmBulletY',183,i);w('MmBulletAge',0,i);w('MmBulletDir',1,i)
 end
 for i=0,5 do
  w('EnemyMetasprite',L.METASPRITE_KOOPA_WALKING_1,i)
  w('Enemy_X_Position',100+20*i,i);w('Enemy_PageLoc',0,i)
  w('Enemy_Y_Position',176,i);w('Enemy_Y_HighPos',1,i);w('Enemy_SprAttrib',1,i)
 end
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if r('CurrentBank')%128~=4 or frame<590 or frame>680 then return end
 draws=draws+1
 assert(r('GuestOamRotationActive')==1 and r('RgOamPlayerStart')>=16,'Mega Man allocates every shot before the body and enemies')
 local pattern={}
 for logical=0,r('RgOamPlayerStart')-1,4 do
  local o=(logical+r('RgOamRotation'))%256
  local id=key(o);all[id]=true
  local row=r('Sprite_Y_Position',o)+8
  local rank=0
  for p=0,o,4 do
   local y=r('Sprite_Y_Position',p)+1
   if y<=row and y+16>row then rank=rank+1 end
  end
  if rank<=8 then seen[id]=true;pattern[#pattern+1]=id end
 end
 orders[table.concat(pattern,',')]=true
end,emu.callbackType.exec,L.RosterOamReady)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==681 then
  local parts,visible,patterns=0,0,0
  for _ in pairs(all) do parts=parts+1 end
  for _ in pairs(seen) do visible=visible+1 end
  for _ in pairs(orders) do patterns=patterns+1 end
  assert(draws>30 and parts>=4 and patterns>2,'Crowded buster row changes hardware priority')
  assert(parts==visible,'Every normal/charged shot part receives hardware visibility: '..visible..'/'..parts)
  print('PASS Mega Man reserves shots before enemies and rotates all shot parts through crowded scanline visibility: '..visible..' parts, '..patterns..' priority patterns')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
