-- Explicit movement arena, not a level-clear proof. No grants or physics writes
-- after setup: ordinary A / Down+B / directions drive the actual game handlers.
local frame=0
local normalMin,pogoMin=255,255
local moving,landed=false,false
local out=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-native-movement.csv','w'))
out:write('frame,x,y,state,pogo,status,vy_hi,vy_mid,crouch\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function reset(ledge)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)end end
 if ledge then for row=96,160,16 do for col=11,13 do w('Block_Buffer_1',0x54,row+col);w('MmSolidTerrain',1,row+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('Player_X_Position',ledge and 112 or 96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('TimerControl',0)
 w('InjuryTimer',0);w('StarInvincibleTimer',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
emu.addEventCallback(function()
 local b={down=frame==80,right=frame==100 or frame==120,start=frame==200}
 if frame>=640 and frame<700 then b.a=true end
 if frame>=780 and frame<820 then b.down=true;b.b=true end
 if frame>=850 and frame<862 then b.a=true end
 if frame>=865 and frame<1070 then b.down=true;b.b=true end
 if frame>=1140 and frame<1180 then b.down=true;b.right=true end
 if frame>=1550 and frame<1560 then b.a=true end
 if frame>=1220 and frame<1232 then b.a=true end
 if frame>=1236 and frame<1500 then
  b.down=true;b.b=true
  if not moving and r('ScPogo')~=0 and r('MmVY',2)>=128 and r('Player_Y_Position')>=160 then moving=true end
  if moving then b.right=r('Player_X_Position')<184 end
  if moving and r('Player_X_Position')>=176 and r('Player_Y_Position')<=96 then landed=true end
  if landed then b.down=false;b.b=false end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==620 then assert(r('SelectedCharacter')==12 and r('GameEngineSubroutine')==8,'Scrooge enters movement arena');reset(false)end
 if frame>=640 and frame<750 then normalMin=math.min(normalMin,r('Player_Y_Position'))end
 if frame==750 then assert(normalMin==118,'Native ordinary jump must rise58px; got '..(176-normalMin));print('PASS Scrooge native58px ordinary jump')end
 if frame==830 then assert(r('Player_State')==0 and r('Player_Y_Position')==176 and r('ScPogo')==0,'Native ground Down+B does not initiate pogo');print('PASS Scrooge pogo requires airborne engagement')end
 if frame>=930 and frame<1070 then pogoMin=math.min(pogoMin,r('Player_Y_Position'))end
 if frame==1080 then assert(pogoMin==92,'Native pogo must rise84px; got '..(176-pogoMin));assert(r('ScPogo')==0,'Pogo release works');print('PASS Scrooge native84px pogo and release')end
 if frame==1120 then reset(false)end
 if frame==1180 then assert(r('Player_X_Position')==96 and r('RgCrouch')~=0,'Native duck+Right crouches in place');print('PASS Scrooge native stationary crouch')end
 if frame==1200 then reset(true)end
 if frame>=620 then
  out:write(table.concat({frame,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('ScPogo'),r('PlayerStatus'),r('MmVY',2),r('MmVY',1),r('RgCrouch')},',')..'\n')
 end
 if frame==1540 then
  assert(moving and landed,'Unpowered Scrooge reaches an80px ledge using his stronger native pogo')
  assert(r('Player_Y_Position')==96 and r('Player_State')==0 and r('PlayerStatus')==0,'Unpowered traversal settles on the ledge without a granted powerup')
  assert(r('GameEngineSubroutine')==8,'Scrooge remains playable')
  print('PASS Scrooge unpowered80px ledge escape with genuine A, Down+B and Right controls')
  reset(false)
 end
 if frame==1562 then
  assert(r('MmVY',2)<128 and r('Player_Y_Position')>128,'Releasing ordinary A stops ascent early')
  assert(r('XgRise')==0,'Variable jump origin flag clears after release')
  print('PASS Scrooge native short jump releases upward motion');out:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
