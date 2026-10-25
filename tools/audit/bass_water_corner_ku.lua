-- Explicit injected coral arena after real menu startup; NOT a campaign replay.
local frame, seeded, age = 0, false, 0
local repaired = L.BassSophiaTerrainDispatch ~= nil
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local trace=assert(io.open(OUTPUT..ROM_NAME..'-bass-corner-arena.csv','w'))
trace:write('age,x,y,state,vy,subY,wall\n')
local minimum,maximum,lastX,jumps = 65535,0,nil,0
local function seed()
 w('OperMode',1);w('OperMode_Task',3);w('CrossoverMenuState',0)
 w('SelectedCharacter',9);w('CrossoverBehaviorVersion',0)
 w('WorldNumber',1);w('LevelNumber',1);w('AreaNumber',1);w('AreaType',0);w('SwimmingFlag',1);w('MmUnderwater',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('Player_State',1)
 w('PlayerStatus',0);w('PlayerSize',1)
 w('Player_X_Position',2481);w('Player_PageLoc',2481//256)
 w('Player_Y_Position',56);w('Player_Y_HighPos',1)
 w('Player_X_Speed',22);w('Player_Y_Speed',255)
 w('MmVX',0,0);w('MmVX',96,1);w('MmVX',1,2)
 -- Observed ascent approaching the coral's underside: apex remains below
 -- its top. The correct response is to retain the real vertical side wall.
 w('MmVY',51,0);w('MmVY',78,1);w('MmVY',255,2)
 w('MmXFraction',0,0);w('MmXFraction',96,1)
 w('MmYFraction',183,0);w('MmYFraction',52,1)
 w('RgPreviousButtons',128);w('XgJumpUsed',1);w('RgCrouch',0)
 w('A_B_Buttons',128);w('PreviousA_B_Buttons',128);w('MmJumpReleased',0);w('MmFrictionYActive',0)
 local camera=2401
 w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256)
 w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2);w('GameTimerExpiredFlag',0)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 local function cell(x,y)
  local base=((x//256)%2==0)and L.Block_Buffer_1 or L.Block_Buffer_2
  emu.write(base+(x//16)%16+y-32,105,emu.memType.nesDebug)
 end
 for x=2496,2528,16 do cell(x,80)end
 for y=96,192,16 do cell(2496,y)end
 for x=2304,2559,16 do cell(x,208)end
 seeded=true
end
emu.addMemoryCallback(function()
 if not seeded and frame>=620 then seed()end
end,emu.callbackType.exec,L.PauseSkip)
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==240,
  down=frame==80,right=(frame>=100 and frame<160 and(frame-100)%20==0)or seeded,a=seeded,up=seeded},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if seeded then
  age=age+1
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  minimum=math.min(minimum,x);maximum=math.max(maximum,x)
  if lastX and math.abs(x-lastX)>=8 then jumps=jumps+1 end
  lastX=x
  trace:write(table.concat({age,x,r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),r('MmYFraction',1),r('XgWallContact')},',')..'\n')
  if repaired then assert(x<=2482,'Bass cannot pass the quantized coral wall through the missing bottom sample: '..x)end
  if age==80 then
   trace:close()
   if repaired then assert(jumps==0 and maximum<=2482,'No large sideways ejection and native quantized wall contact persists')
   else assert(jumps>=2 or maximum>=2496,'Original negative control must exhibit the missed wall contact')end
   local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-corner-arena.json','w'))
   f:write(string.format('{"passed":true,"repaired":%s,"minimumX":%d,"maximumX":%d,"sidewaysJumps":%d,"frames":%d,"injected_arena":true,"controller_route":false}\n',tostring(repaired),minimum,maximum,jumps,age));f:close()
   print('PASS Bass native coral arena repaired='..tostring(repaired)..' x='..minimum..'..'..maximum..' jumps='..jumps);emu.stop(0)
  end
 end
 if frame>800 then assert(false,'Bass coral arena timed out')end
end,emu.eventType.endFrame)
