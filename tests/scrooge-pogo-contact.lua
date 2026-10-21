-- Explicit durable-body contact arena. No invincibility grant: a valid pogo
-- must rebound safely before the surviving target's ordinary body hurts us.
local frame,hits,previous,phase=0,0,300,0
local ordinaryInjury,immuneBaselineInjury,adjacentInjury,adjacentHit=false,false,false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-pogo-contact.csv','w'))
out:write('frame,phase,y,health,vy,injury,engine,hits,immuneId,immuneY,immuneOffscreen,receipt,flash0,flash1,pogo\n')
local function setup(parity)
 phase=parity+1;hits=0;previous=300
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col);w('MmSolidTerrain',1,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',112);w('Player_Y_HighPos',1)
 w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',1);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('SmBombHits',0)
 w('InjuryTimer',0);w('StarInvincibleTimer',0);w('StompTimer',0);w('TimerControl',0);w('GameEngineSubroutine',8);w('FrameCounter',parity)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',1,2)
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',0)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',160);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0);w('Enemy_CollisionBits',0)
 w('MmEnemyHealthLo',44);w('MmEnemyHealthHi',1)
end
local function immuneTarget()
 w('Enemy_Flag',1,1);w('Enemy_ID',0x0c,1);w('Enemy_State',0,1);w('Enemy_BoundBoxCtrl',9,1)
 w('Enemy_X_Position',128,1);w('Enemy_PageLoc',0,1);w('Enemy_Y_Position',154,1);w('Enemy_Y_HighPos',1,1)
 w('Enemy_X_Speed',0,1);w('Enemy_Y_Speed',0,1);w('Enemy_Y_MoveForce',0,1);w('EnemyIntervalTimer',255,1)
 w('EnemyOffscrBitsMasked',0,1);w('Enemy_CollisionBits',0,1)
end
emu.addEventCallback(function()
 local pogo=(frame>=640 and frame<1400)or(frame>=1440 and frame<1550)
 emu.setInput({down=frame==80 or pogo,right=frame==100 or frame==120,start=frame==200,b=pogo},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==640 then assert(r('SelectedCharacter')==12,'Scrooge selected');setup(0)end
 if frame==1020 then setup(1)end
 if phase>0 and((frame>640 and frame<1000)or(frame>1020 and frame<1380))then
  local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
  if hp<previous then
   assert(previous-hp==100,'Each contact applies exactly100damage')
   assert(r('MmVY',2)>=128 and r('Player_State')==1,'Successful body-sized pogo immediately rebounds')
   assert(r('InjuryTimer')==0 and r('GameEngineSubroutine')==8,'Successful pogo contact wins over the durable target body without a granted invincibility timer')
   hits=hits+1;previous=hp
  end
  if r('Enemy_Flag')>0 and r('Enemy_State')<32 then
   -- Only the target is held in place; avatar position/velocity stay genuine.
   w('Enemy_X_Position',128);w('Enemy_Y_Position',160);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',0)
  end
 end
 if frame==1000 or frame==1380 then
  assert(hits==3 and(r('Enemy_Flag')==0 or r('Enemy_State')>=32),'Three real descents defeat the durable body target in parity phase '..phase)
  assert(r('InjuryTimer')==0 and r('GameEngineSubroutine')==8,'Durable pogo remains healthy/playable throughout')
  print('PASS Scrooge durable body-sized pogo contact priority, native collision parity '..(phase-1))
 end
 if frame==1400 then
  setup(0);phase=3;w('Player_Y_Position',148);w('MmVY',250,2);w('Player_Y_Speed',250)
 end
 if phase==3 and frame>1400 and frame<1430 then
  ordinaryInjury=ordinaryInjury or r('InjuryTimer')>0 or r('GameEngineSubroutine')==11
 end
 if frame==1430 then assert(ordinaryInjury,'Ordinary rising body contact remains harmful when pogo is inactive');print('PASS Scrooge inactive pogo does not grant body immunity')end
 if frame==1440 then
  setup(1);phase=4;w('Player_Y_Position',132);w('Enemy_Flag',0);immuneTarget()
 end
 if phase==4 and frame>1440 and frame<1480 then
  immuneBaselineInjury=immuneBaselineInjury or r('InjuryTimer')>0 or r('GameEngineSubroutine')==11
  w('Enemy_X_Position',128,1);w('Enemy_Y_Position',154,1);w('Enemy_Y_HighPos',1,1);w('Enemy_X_Speed',0,1);w('Enemy_Y_Speed',0,1)
 end
 if frame==1480 then assert(immuneBaselineInjury,'Onscreen native Podoboo baseline must hurt an unsupported pogo before testing scoped immunity');print('PASS Scrooge immune Podoboo baseline really causes injury')end
 if frame==1500 then
  setup(1);phase=5;w('Player_Y_Position',132);immuneTarget()
 end
 if phase==5 and frame>1500 and frame<1550 then
  adjacentHit=adjacentHit or r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')<300
  adjacentInjury=adjacentInjury or r('InjuryTimer')>0 or r('GameEngineSubroutine')==11
  for slot=0,1 do
   w('Enemy_X_Position',128,slot);w('Enemy_Y_Position',slot==0 and 160 or 154,slot);w('Enemy_Y_HighPos',1,slot);w('Enemy_X_Speed',0,slot);w('Enemy_Y_Speed',0,slot)
  end
 end
 if frame==1550 then
  out:flush()
  assert(adjacentHit and adjacentInjury,'A real pogo strike does not protect contact with the adjacent immune Podoboo: hit='..tostring(adjacentHit)..' injured='..tostring(adjacentInjury))
  print('PASS Scrooge successful pogo protects only its struck susceptible target')
  out:close();print('PASS Scrooge native pogo/enemy contact priority, both parities and scoped injury guards');emu.stop(0);return
 end
 if phase>0 then
  out:write(table.concat({frame,phase,r('Player_Y_Position'),r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi'),r('MmVY',2),r('InjuryTimer'),r('GameEngineSubroutine'),hits,r('Enemy_ID',1),r('Enemy_Y_Position',1),r('EnemyOffscrBitsMasked',1),r('ScEnemy'),r('MmEnemyFlash'),r('MmEnemyFlash',1),r('ScPogo')},',')..'\n')
 end
end,emu.eventType.endFrame)
