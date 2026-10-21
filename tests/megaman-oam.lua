-- Exercise changing metasprite sizes with normal input, then injury blink and
-- native contact death. No OAM bytes are patched by this test.
local frame=0
local checked=0
local poses={}
local blinkFrames=0
local deathChecked=false
local rejectionSnapshot
local rejectionChecked=false
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function rom(bank,address) return emu.read(bank*0x2000+address%0x2000,emu.memType.nesPrgRom) end
local function size(id)
  -- Pointer tables live in the renderer's $a000 bank; guest data is in $c000.
  local pointer=rom(4,L.MetaspriteTableRightLo+id)+256*rom(4,L.MetaspriteTableRightHi+id)
  return rom(12,pointer)
end
local function screenshot(tag)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-'..tag..'.png','wb'))
  f:write(emu.takeScreenshot());f:close()
end
-- A full-buffer fixture exercises atomic rejection of a flipped four-sprite
-- enemy. Setting the allocation cursor models earlier objects filling OAM;
-- the rejected draw must leave every existing byte intact.
emu.addMemoryCallback(function()
  if frame~=724 or rejectionSnapshot or r('CurrentBank')%128~=4 then return end
  local pointer=r('R0')+256*r('R1')
  if pointer<0xa000 or pointer>=0xc000 or emu.read(pointer,emu.memType.nesDebug)<12 then return end
  w('M1',0x80)
  w('CurrentOAMOffset',0xfc)
  rejectionSnapshot={}
  for offset=0,255 do rejectionSnapshot[offset]=r('Sprite_Y_Position',offset) end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()
  if not rejectionSnapshot or rejectionChecked or r('CurrentBank')%128~=4 then return end
  for offset=0,255 do
    assert(r('Sprite_Y_Position',offset)==rejectionSnapshot[offset],
      'Rejected flipped metasprite must preserve prior OAM byte '..offset)
  end
  rejectionChecked=true
  print('PASS OAM overflow rejects a flipped enemy without corrupting earlier sprites')
end,emu.callbackType.exec,L.DontShiftPositions)
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or (frame>=500 and frame<560),start=frame==120,
    a=(frame>=530 and frame<555) or frame==620,b=frame==520 or frame==580,
    down=frame==620 or frame==740},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 and frame<780 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame>=490 and frame<775 then
    local id=r('ObjectMetasprite')
    local used=id==0 and 0 or size(id)
    poses[id]=true
    assert(used<=40 and used%4==0,'Player metasprite fits the reserved ten entries')
    for offset=used,39,4 do
      local physical=(offset+r('RgOamPlayerStart')+r('RgOamRotation'))%256
      if r('Sprite_Y_Position',physical)~=0xf8 then screenshot('oam-stale-reproduction') end
      assert(r('Sprite_Y_Position',physical)==0xf8,
        'Stale player OAM at frame '..frame..', slot '..(offset/4)..', pose '..id..', bytes used '..used)
    end
    if id==0 then blinkFrames=blinkFrames+1 end
    checked=checked+1
  end
  if frame==550 then screenshot('oam-jump-fixed') end
  if frame==650 then w('InjuryTimer',60) end
  if frame==724 then
    w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_State',0)
    w('Enemy_X_Position',200);w('Enemy_PageLoc',0)
    w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
    w('Enemy_BoundBoxCtrl',3);w('Enemy_X_Speed',0)
  end
  if frame==775 then
    local count=0;for _ in pairs(poses) do count=count+1 end
    assert(count>=6,'Replay exercises different body and arm poses')
    assert(blinkFrames>10,'Injury blink fully hides the player reservation')
    assert(checked>250,'OAM cleanup is checked across consecutive animation frames')
    assert(rejectionChecked,'The full-buffer rejection fixture was exercised')
    print('PASS no stale OAM across running, jumping, shooting, sliding, idle and injury blink')
  end
  if frame==790 then
    w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
    w('Enemy_X_Position',r('Player_X_Position'));w('Enemy_PageLoc',r('Player_PageLoc'))
    w('Enemy_Y_Position',r('Player_Y_Position'));w('Enemy_Y_HighPos',1)
    w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
    w('InjuryTimer',0)
  end
  if frame>790 and r('MmDeathFlag')~=0 and r('MmDeathAge')==10 then
    local visible=0
    for offset=0,95,4 do if r('Sprite_Y_Position',(offset+r('RgOamRotation'))%256)<240 then visible=visible+1 end end
    assert(visible==24,'All twelve death particles retain their two OAM entries: '..visible)
    deathChecked=true
    screenshot('oam-death-fixed')
    print('PASS death particles survive player cleanup without missing OAM entries')
  end
  if frame==850 then
    assert(deathChecked,'Native contact death was exercised')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
