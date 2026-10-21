-- Explicit durable-enemy fixture. A successful pogo hit must rebound even
-- while the enemy survives; the next descent can apply its own single hit.
local frame,hits=0,0
local previousHealth=300
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80 or(frame>=640 and frame<950),right=frame==100 or frame==120,start=frame==200,
  b=frame>=640 and frame<950},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==640 then
  assert(r('SelectedCharacter')==12,'Scrooge is selected')
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i)end
  w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',112);w('Player_Y_HighPos',1)
  w('Player_State',2);w('Player_X_Speed',0);w('Player_Y_Speed',1);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('ScAttack',0);w('ScPogo',0);w('ScPrevious',0);w('SmBombHits',0);w('SmSlot',0)
  w('InjuryTimer',0);w('TimerControl',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('MmVY',1,2)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',192);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('MmEnemyHealthLo',44);w('MmEnemyHealthHi',1)
 end
 if frame>=640 and frame<950 and r('Enemy_Flag')>0 and r('Enemy_State')<32 then
  w('Enemy_X_Position',128);w('Enemy_Y_Position',192);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if frame>=641 and frame<950 then
  local health=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
  if health<previousHealth then
   assert(previousHealth-health==100,'Each independent pogo descent applies exactly one hit')
   assert(r('MmVY',2)>=128 and r('Player_State')==1,'Successful pogo hit immediately rebounds while the enemy may survive')
   hits=hits+1;previousHealth=health
   print('PASS Scrooge pogo strike '..hits..' rebounds at health '..health)
  end
 end
 if frame==950 then
  assert(hits==3 and(r('Enemy_Flag')==0 or r('Enemy_State')>=32),'Three rebounds defeat the durable enemy without falling through it')
 end
 if frame==960 then
  assert(r('ScPogo')==0 and r('GameEngineSubroutine')==8,'Releasing pogo restores ordinary playable movement')
  print('PASS Scrooge durable-enemy pogo: one hit per descent, nonlethal rebounds, next bounce can hit again, final defeat');emu.stop(0)
 end
end,emu.eventType.endFrame)
