-- Independent real 2-2 native Mario/Luigi fall and respawn timing. Initial
-- below-room setup only; no avatar writes after the fall begins.
local character=assert(NATIVE_BROTHER)
local frame,started=0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-native-water-pit-'..character..'.csv','w'))
out:write('age,x,y,yHigh,state,vx,vy,engine,mode,task,lives,deathMusic,eventMusic\n')
emu.addEventCallback(function()emu.setInput({select=character==8 and frame==180,start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',1);w('LevelNumber',1);w('AreaNumber',2)end
 if frame==640 then
  assert(r('SelectedCharacter')==character and r('SwimmingFlag')==1,'Independent control starts real 2-2')
  for i=0,5 do w('Enemy_Flag',0,i);w('Whirlpool_PageLoc',0,i)end
  w('FrameCounter',0);w('Player_X_Position',88);w('Player_PageLoc',0);w('Player_Y_Position',64);w('Player_Y_HighPos',2)
  w('Player_State',2);w('PlayerStatus',2);w('PlayerSize',0);w('Player_X_Speed',0);w('Player_Y_Speed',4)
  w('Player_X_MoveForce',0);w('SprObject_X_MoveForce',0);w('Player_Y_MoveForce',0);w('Player_YMoveForceFractional',0)
  w('TimerControl',0);w('GameEngineSubroutine',8);w('MarioWaterActive',0);w('MarioWaterPulled',0)
  w('DeathMusicLoaded',0);w('CloudTypeOverride',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('MmDeathFlag',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  started=true
 elseif started then
  out:write(table.concat({frame-640,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task'),r('NumberofLives'),r('DeathMusicLoaded'),r('EventMusicBuffer')},',')..'\n')
  assert(r('MmDeathFlag')==0,'Native pit uses the native engine')
  if r('NumberofLives')==1 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   out:close();print('PASS native brother '..character..' real water pit respawn after '..(frame-640)..' frames');emu.stop(0);return
  end
 end
 if frame==2100 then assert(false,'Native water pit never respawned')end
end,emu.eventType.endFrame)
