-- Explicit offscreen water arena after a real menu/room entrance. Ordinary
-- held Right must still reach guest movement above the viewport, matching
-- Character's unrestricted buttons/above-water branch in the pinned source.
-- Mario/Luigi retain their native SMB water cutoff as control cases.
local c=assert(WATER_CONTROL_CHARACTER)
local frame,depth,checks=0,0,0
local pending=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()depth=depth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if frame>=550 and depth==0 and r('CurrentBank')%128==1 and r('GameEngineSubroutine')==8 and r('Player_Y_HighPos')==0 then
  -- The setup can occur after a poll, and a catch-up GameLoop may reuse the
  -- native parser's cleared byte before the next NMI. Observe only updates
  -- that actually enter with the new ordinary held input latched.
  if(r('SavedJoypadBits')&1)==0 then return end
  pending=true
 end
end,emu.callbackType.exec,L.PlayerCtrlRoutine)
emu.addMemoryCallback(function(_,v)
 if not pending or depth~=0 then return end
 pending=false;checks=checks+1
 local expected=(c==0 or c==8)and 0 or 1
 assert(v==expected,'Upper-water controller parsing for character '..c..': Right='..v..', expected '..expected..', PC='..string.format('%04x',emu.getState()['cpu.pc'])..', bank='..r('CurrentBank')..', frame='..frame..', YHigh='..r('Player_Y_HighPos')..', raw='..r('SavedJoypadBits'))
 assert((r('SavedJoypadBits')&1)==expected,'Saved ordinary input follows the same upper-water rule')
end,emu.callbackType.write,L.Left_Right_Buttons)
emu.addEventCallback(function()
 local slot=c==12 and 8 or c==8 and 0 or c
 emu.setInput({down=slot>=6 and frame==80,
  right=frame>=550 or(slot>=6 and frame>=100 and frame<100+(slot-6)*20 and(frame-100)%20==0)or(slot<6 and frame>=80 and frame<80+slot*20 and(frame-80)%20==0),
  select=c==8 and frame==180,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',1);w('LevelNumber',1);w('AreaNumber',2)end
 if frame==550 then
  assert(r('SelectedCharacter')==c and r('AreaType')==0 and r('GameEngineSubroutine')==8,'Real selected-character water room')
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',250);w('Player_Y_HighPos',0)
  w('Player_State',1);w('Player_Y_Speed',0);w('Player_X_Speed',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 end
 if frame==600 then
  assert(checks>0,'Real player-control updates exercised above viewport')
  print('PASS upper-water ordinary controller input, character '..c..', '..checks..' updates; native Mario/Luigi cutoff preserved')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
