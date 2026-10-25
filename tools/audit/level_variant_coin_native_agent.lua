-- Authored RAM arena exercising real jump/head/bounce/coin/PPU calls.
-- This is a native component fixture, not an ordinary controller route.
local frame,phase,age=0,0,0
local coins,bumps=0,0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local target=208+3+7*16 -- World5-2 native constructor cell147,9.
local log=assert(io.open(OUTPUT..ROM_NAME..'-source-coin-arena.csv','w'));log:write('frame,phase,age,x,y,state,yspeed,eng,tile,tally,coins,size,status,r0,r2,r6,r7\n')
local function seed(easy)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 w('Block_Buffer_1',easy and 0x6e or 0x58,target)
 w('SelectedCharacter',0);w('CrossoverBehaviorVersion',easy and 0 or 1)
 w('OperMode',1);w('OperMode_Task',3);w('CrossoverMenuState',0)
 w('WorldNumber',4);w('LevelNumber',1);w('AreaNumber',1);w('AreaPointer',0x31);w('AreaType',1)
 w('Player_X_Position',40);w('Player_PageLoc',9);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0)
 w('PlayerSize',0);w('PlayerStatus',1);w('CrouchingFlag',0);w('GameEngineSubroutine',8)
 w('ScreenLeft_X_Pos',144);w('ScreenLeft_PageLoc',8);w('ScreenRight_X_Pos',143);w('ScreenRight_PageLoc',9)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('EnemyDataLow',0);w('EnemyDataHigh',0x60);emu.write(0x6000,0xff,emu.memType.nesDebug)
 w('VRAM_Buffer1_Offset',0);w('VRAM_Buffer1',0);w('VRAM_Buffer2_Offset',0);w('VRAM_Buffer2',0);w('VRAM_Buffer_AddrCtrl',0)
 w('TimerControl',0);w('BlockBounceTimer',0);w('BrickCoinTimer',0);w('BrickCoinTimerFlag',0);w('CoinTally',0)
 w('PreviousA_B_Buttons',0);w('A_B_Buttons',0);age=0
end
emu.addMemoryCallback(function()
 if frame>=600 and phase==0 then phase=1;seed(false)
 elseif phase==2 then phase=3;seed(true)end
end,emu.callbackType.exec,L.PauseSkip)
emu.addMemoryCallback(function()if phase==1 then coins=coins+1 end end,emu.callbackType.exec,L.CoinBlock)
emu.addMemoryCallback(function()if phase==3 then bumps=bumps+1 end end,emu.callbackType.exec,L.BumpOrClimb)
emu.addEventCallback(function()
 local input={start=frame==60 or frame==240}
 if phase==1 or phase==3 then input.a=age>=8 and age<30 or age>=80 and age<102 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==1 or phase==3 then
  age=age+1
  log:write(table.concat({frame,phase,age,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),r('GameEngineSubroutine'),r('Block_Buffer_1',target),r('CoinTally'),coins,r('PlayerSize'),r('PlayerStatus'),r('R0'),r('R2'),r('R6'),r('R7')},',')..'\n');log:flush()
  if age==140 then
   if phase==1 then
    assert(coins==1 and r('CoinTally')==1,'Hard source constructor emits exactly one coin across two real jumps; coins='..coins..' tally='..r('CoinTally')..' tile='..r('Block_Buffer_1',target))
    assert(r('Block_Buffer_1',target)==0xc4,'Hard constructor becomes the native empty block')
    phase=2
   else
    assert(r('CoinTally')==0 and r('Block_Buffer_1',target)==0x6e,'Easy source constructor remains a solid brick without a pickup')
    assert(bumps>0,'Easy jump actually touches the solid brick')
    local f=assert(io.open(OUTPUT..ROM_NAME..'-source-coin-arena.json','w'));f:write('{"passed":true,"hard_coins":'..coins..',"easy_bumps":'..bumps..',"native_frames":'..frame..'}\n');f:close()
    print('PASS native source coin constructor, two hard jumps, easy solid head contact; no ordinary route claim');emu.stop(0)
   end
  end
 end
 if frame>1000 then assert(false,'Native source coin arena timed out')end
end,emu.eventType.endFrame)
