local frame=0
local hits=0
local respawned=false
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120,b=frame==520},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==500 then
    for i=0,5 do w('Enemy_Flag',0,i) end
    w('Enemy_Flag',1); w('Enemy_ID',6); w('Enemy_State',0)
    w('Enemy_X_Position',r('Player_X_Position')+64)
    w('Enemy_PageLoc',r('Player_PageLoc'))
    w('Enemy_Y_Position',r('Player_Y_Position')+8)
    w('Enemy_Y_HighPos',1); w('Enemy_X_Speed',0); w('Enemy_Y_Speed',0)
    w('Enemy_BoundBoxCtrl',9)
  end
  if frame==560 then
    assert(r('MmEnemyHealthLo')==50,'One normal shot leaves the 2.02 Goomba with 50 health')
    print('PASS enemy survives the first buster hit')
  end
  if frame==580 then
    -- Place the player just below a pit; let the native death and life-loss
    -- sequence run to completion instead of directly triggering a respawn.
    w('Player_Y_HighPos',2); w('Player_Y_Position',0x40)
    w('Player_State',2); w('Player_Y_Speed',4)
  end
  if frame>600 and frame<1100 and r('GameEngineSubroutine')==8 and r('NumberofLives')==1 and r('Player_Y_HighPos')==1 then
    respawned=true
  end
  if frame==1100 then
    assert(respawned,'Native pit death returns to player control with one life lost')
    assert(r('SelectedCharacter')==1,'Mega Man selection survives death/respawn')
    print('PASS pit death, life loss, respawn, character persistence')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
