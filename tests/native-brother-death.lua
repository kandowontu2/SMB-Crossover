-- Independent native Mario/Luigi enemy-contact death control. Initial flat
-- room/enemy setup only; death motion and timing are actual engine behavior.
local character=assert(NATIVE_BROTHER)
local frame,start=0,nil
local rose=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-native-death-'..character..'.csv','w'))
out:write('age,x,y,yHigh,state,vx,vy,yForce,yFraction,timer,engine,lives\n')
emu.addEventCallback(function()emu.setInput({select=character==8 and frame==180,start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==character,'Real menu selects native death control')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('PlayerStatus',0);w('PlayerSize',1);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('PlayerFacingDir',1)
  w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('MmDeathFlag',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_PageLoc',0);w('Enemy_X_Position',120)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0)
 end
 if frame>550 and not start and r('GameEngineSubroutine')==11 then start=frame end
 if start then
  for i=0,5 do w('Enemy_Flag',0,i)end
  local age=frame-start
  out:write(table.concat({age,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('Player_Y_MoveForce'),r('Player_YMoveForceFractional'),r('TimerControl'),r('GameEngineSubroutine'),r('NumberofLives')},',')..'\n')
  rose=rose or r('Player_Y_HighPos')==1 and r('Player_Y_Position')<170
  assert(r('MmDeathFlag')==0,'Native brother death never enters the guest velocity integrator')
  if r('GameEngineSubroutine')==6 then
   assert(rose,'Native death arc rises before falling')
   out:close();print('PASS native brother '..character..' real enemy-contact death arc and life-loss transition');emu.stop(0);return
  end
 end
 if frame==1150 then assert(false,'Native brother death did not finish')end
end,emu.eventType.endFrame)
