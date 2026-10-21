-- Explicit native Bowser front/rear arena, not a controller-only clear.
-- Only the boss AI position/facing is pinned; actual body boxes, duplication,
-- damage, defeat and Scrooge's controller-driven movement execute normally.
local frame,index,hits=0,0,0
local current,previous
local cases={}
for _,dir in ipairs({1,2})do for _,part in ipairs({'front','rear'})do for parity=0,1 do
 cases[#cases+1]={dir=dir,part=part,parity=parity}
end end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-pogo-bowser.csv','w'))
out:write('frame,case,facing,part,parity,playerY,health,engine,injury,hits,frontTop,rearTop,rearFlag\n')
local function setup(q)
 current=q;hits=0;previous=300
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col);w('MmSolidTerrain',1,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i);w('Enemy_State',0,i)end
 local x=q.part=='front' and(q.dir==1 and 136 or 120)or(q.dir==1 and 104 or 152)
 w('Player_X_Position',x);w('Player_PageLoc',0);w('Player_Y_Position',112);w('Player_Y_HighPos',1)
 w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',1);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('SmBombHits',0);w('ScEnemy',0)
 w('InjuryTimer',0);w('StarInvincibleTimer',0);w('StompTimer',0);w('TimerControl',0);w('GameEngineSubroutine',8);w('FrameCounter',q.parity)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',1,2)
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',0x2d);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',10)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',160);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0);w('Enemy_CollisionBits',0)
 w('MmEnemyHealthLo',44);w('MmEnemyHealthHi',1)
 w('Enemy_Flag',0x80,1);w('Enemy_ID',0x2d,1);w('Enemy_BoundBoxCtrl',10,1)
 w('Enemy_X_Position',q.dir==1 and 112 or 144,1);w('Enemy_PageLoc',0,1);w('Enemy_Y_Position',168,1);w('Enemy_Y_HighPos',1,1)
 w('BowserFront_Offset',0);w('DuplicateObj_Offset',1);w('BowserHitPoints',5)
 w('BowserBodyControls',0);w('BowserFeetCounter',32);w('BowserMovementSpeed',0);w('BowserOrigXPos',128);w('MaxRangeFromOrigin',32)
 w('EnemyFrameTimer',255);w('BowserFireBreathTimer',255);w('Enemy_MovingDir',q.dir)
end
emu.addMemoryCallback(function()
 if not current or r('CurrentBank')%128~=0 or r('Enemy_State')~=0 then return end
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',160);w('Enemy_Y_HighPos',1)
 w('Enemy_MovingDir',current.dir)
end,emu.callbackType.exec,assert(L.BowserGfxHandler))
emu.addEventCallback(function()
 emu.setInput({down=frame==80 or frame>=640,right=frame==100 or frame==120,start=frame==200,b=frame>=640},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if current then
  local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
  out:write(table.concat({frame,index,current.dir,current.part,current.parity,r('Player_Y_Position'),hp,r('GameEngineSubroutine'),r('InjuryTimer'),hits,r('BoundingBox_UL_Corner',5),r('BoundingBox_UL_Corner',9),r('Enemy_Flag',1)},',')..'\n');out:flush()
  assert(r('InjuryTimer')==0 and r('GameEngineSubroutine')==8,'Native Bowser '..current.part..' contact must pogo before body injury: frame='..frame..' health='..hp)
  if hp<previous then
   assert(previous-hp==100,'Bowser front/rear contact applies one100damage hit to the real boss')
   assert(r('MmVY',2)>=128,'Real boss contact immediately rebounds')
   hits=hits+1;previous=hp
  end
 end
 if frame>=640 and(frame-640)%220==0 then
  if current then
   assert(hits==3 and(r('Enemy_Flag')==0 or r('Enemy_State')>=32),'Three actual descents defeat the real Bowser slot without double-hitting its duplicate')
   print('PASS Scrooge native Bowser '..current.part..' pogo, facing '..current.dir..', parity '..current.parity)
  end
  index=index+1
  if not cases[index]then out:close();print('PASS Scrooge native Bowser front/rear pogo contact, both facings and collision parities');emu.stop(0);return end
  setup(cases[index])
 end
end,emu.eventType.endFrame)
