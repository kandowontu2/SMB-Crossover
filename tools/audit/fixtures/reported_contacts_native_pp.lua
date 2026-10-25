-- Seeded native1-1 diagnostics: inputs and actual game collision/update paths.
local frame,phase,entered=0,0,nil
local currentStage,stageAt=0,0
local blocks,inhales,headBreaks,yoyoBreaks,shots=0,0,0,0,0
local syphaMin,syphaMaxStep,priorY=255,0,nil
local log=assert(io.open(OUTPUT..'states.csv','w'));log:write('frame,stage,t,x,y,state,block0,block1,mouth,hp,shots\n')
local writes=assert(io.open(OUTPUT..'x-writes.csv','w'));writes:write('frame,stage,pc,bank,address,value\n')
local walls=assert(io.open(OUTPUT..'walls.csv','w'));walls:write('frame,x,y,side,tile,row,column,eb,speed\n')
local weapons=assert(io.open(OUTPUT..'weapons.csv','w'));weapons:write('frame,stage,engine,timer,death,attack,pressed,weapon,shot0,shot1,shot2,shot3,shot4,shot5,x5,y5,dir\n')
local probes=assert(io.open(OUTPUT..'probes.csv','w'));probes:write('frame,x,y,tile,btype,slot,pkind\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function cell(x,y)return r('Block_Buffer_1',(x//256)%2*208+(y//16-2)*16+x%256//16)end
local function image(tag)
 local b=emu.getScreenBuffer();local f=assert(io.open(OUTPUT..tag..'.rgba','wb'))
 for i=1,#b,8 do f:write(string.pack('<I4I4I4I4I4I4I4I4',table.unpack(b,i,i+7)))end
 f:close()
end
local function reset(x,camera)
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('MmOldX',x%256)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
 w('Player_X_Speed',0);w('Player_X_Scroll',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',camera%256);w('ScreenLeft_PageLoc',camera//256)
 w('ScreenRight_X_Pos',(camera+255)%256);w('ScreenRight_PageLoc',(camera+255)//256)
 w('HorizontalScroll',camera%256);w('InjuryTimer',0);w('TimerControl',0)
 w('Block_State',0,0);w('Block_State',0,1);w('BlockBounceTimer',0)
end
local function begin(stage)
 currentStage=stage;stageAt=frame
 if NAME=='kirby' then
  w('KbHurt',0);w('KbHurtMove',0);w('KbHealth',6);w('KbAction',0);w('KbActionAge',0);w('KbMouth',0);w('KbCopy',0);w('KbCooldown',0)
  if stage==1 then reset(247,128);assert(cell(256,144)~=0,'Native question exists')
  else reset(80,0)end
  if stage==2 then
   w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',116);w('Enemy_PageLoc',0)
   w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0xf8);w('Enemy_Y_Speed',0)
   w('Enemy_MovingDir',2);w('Enemy_BoundBoxCtrl',9)
  elseif stage==3 then w('KbCopy',2)end
 elseif NAME=='mike' then
  if stage==1 then reset(320,160);assert(cell(320,144)==0x51,'Native brick exists')
  else reset(80,0)end
  w('JnHurt',0);w('JnJump',0);w('JnFallFrac',0);w('JnVY',0);w('JnAttack',0)
  if stage==2 then
   -- Explicit seeded brick within grounded yo-yo reach. The actual weapon,
   -- block policy, sound queues, debris and replacement path do all effects.
   local index=(192//16-2)*16+112//16
   w('Block_Buffer_1',0x51,index)
  end
 else
  reset(80,0);w('Cv3JumpActive',0);w('Cv3Climb',0);w('Cv3Bat',0);w('Cv3VyLo',0);w('Cv3VyHi',0)
 end
end
emu.addMemoryCallback(function(address,value)
 if currentStage==0 or NAME~='mike' then return end
 local s=emu.getState();writes:write(table.concat({frame,currentStage,s['cpu.pc'],emu.convertAddress(s['cpu.pc']).address//8192,address,value},',')..'\n');writes:flush()
end,emu.callbackType.write,L.Player_X_Position)
emu.addMemoryCallback(function()
 if NAME~='mike' or currentStage==0 or emu.convertAddress(L.SamusStopAtWallBanked).address//8192~=B.SamusStopAtWallBanked then return end
 walls:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('R0'),r('R3'),r('R2'),r('R6'),r('Local_eb'),r('Player_X_Speed')},',')..'\n');walls:flush()
end,emu.callbackType.exec,L.SamusStopAtWallBanked)
emu.addMemoryCallback(function()
 if NAME~='mike' or currentStage==0 or emu.convertAddress(L.Cv3BlockPoint).address//8192~=B.Cv3BlockPoint then return end
 local x=r('MmProbeX')+256*r('MmProbePage');local y=r('MmProbeY')
 probes:write(table.concat({frame,x,y,cell(x,y),r('MmBulletType'),r('JnSlot'),r('JnShotKind',r('JnSlot'))},',')..'\n');probes:flush()
end,emu.callbackType.exec,L.Cv3BlockPoint)
emu.addEventCallback(function()
 local b={}
 if phase==0 then
  b.start=frame>=60 and frame%12==0
  if frame>=60 and r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and frame%12==0 then
  local i=r('CrossoverMenuIndex');local row=i<12 and i//6 or 2;local target=TARGET_SLOT<12 and TARGET_SLOT//6 or 2
  if row~=target then b.down=true
  elseif i~=TARGET_SLOT then b.right=true
  elseif VARIANT_ADDRESS~=0 and emu.read(VARIANT_ADDRESS,emu.memType.nesDebug)~=VARIANT then b.select=true
  else b.a=true;phase=2 end
 elseif currentStage>0 then
  local t=frame-stageAt
  if NAME=='kirby' then
   if currentStage==1 then b.a=t>=5 and t<40
   elseif currentStage==2 then b.b=t>=5 and t<65;b.right=t>=15 and t<35
   else b.b=t==5 end
  elseif NAME=='mike' then
   if currentStage==1 then b.a=t>=5 and t<40 else b.b=t==5 end
  else b.a=t>=5 and t<50 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=frame;phase=3 end
 if entered and currentStage==0 and frame-entered==15 then begin(1)end
 if currentStage>0 then
  local t=frame-stageAt
  log:write(table.concat({frame,currentStage,t,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('Block_State'),r('Block_State',1),r('KbMouth'),r('KbHealth'),r('KbShotType')},',')..'\n');log:flush()
  if NAME=='mike' then weapons:write(table.concat({frame,currentStage,r('GameEngineSubroutine'),r('TimerControl'),r('MmDeathFlag'),r('JnAttack'),r('JnPressed'),r('JnWeapon'),r('JnShotKind',0),r('JnShotKind',1),r('JnShotKind',2),r('JnShotKind',3),r('JnShotKind',4),r('JnShotKind',5),r('JnShotX',5),r('JnShotY',5),r('PlayerFacingDir')},',')..'\n');weapons:flush()end
  if NAME=='kirby' then
   if currentStage==1 then
    for i=0,1 do
     if r('Block_State',i)~=0 and r('Block_Orig_YPos',i)==112 then
      assert(r('Block_X_Position',i)+256*r('Block_PageLoc',i)==256,'Off-center head bounce stays on its contacted question')
      blocks=blocks+1
     end
    end
   elseif currentStage==2 then
    if r('Enemy_Flag')~=0 and r('KbAction')==1 and r('KbActionAge')==0 then
     assert(r('Enemy_Y_Position')<=184,'Inhaling does not push the walking enemy below ground')
    end
    assert(r('KbHealth')==6,'Active inhale must not damage Kirby from an edible front target')
    if r('KbMouth')~=0 then inhales=inhales+1 end
   else
    for i=0,2 do if r('KbShotType',i)~=0 then shots=shots+1 end end
   end
   if t==30 or t==60 then image('stage'..currentStage..'-'..t)end
   if t==85 and currentStage<3 then begin(currentStage+1)
   elseif t==85 and currentStage==3 then
    assert(blocks>0 and inhales>0 and shots>0,'Each actual Kirby interaction executed: '..blocks..','..inhales..','..shots)
    local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"passed":true,"seeded_native":true,"head_bounce_samples":%d,"mouth_samples":%d,"shot_samples":%d}\n',blocks,inhales,shots));f:close();emu.stop(0)
   end
  elseif NAME=='mike' then
   if r('Block_State')==2 or r('Block_State',1)==2 then
    if currentStage==1 then headBreaks=headBreaks+1 else yoyoBreaks=yoyoBreaks+1 end
   end
   if t==25 or t==45 then image('stage'..currentStage..'-'..t)end
   if t==70 and currentStage==1 then begin(2)
   elseif t==70 then
    assert(headBreaks>0 and yoyoBreaks>0,'Mike breaks a native brick using each requested move: '..headBreaks..','..yoyoBreaks)
    local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"passed":true,"seeded_native":true,"head_break_samples":%d,"yoyo_break_samples":%d}\n',headBreaks,yoyoBreaks));f:close();emu.stop(0)
   end
  else
   local y=r('Player_Y_Position');syphaMin=math.min(syphaMin,y)
   if priorY then syphaMaxStep=math.max(syphaMaxStep,math.abs(y-priorY))end;priorY=y
   if t==25 or t==45 then image('jump-'..t)end
   if t==85 then
    assert(syphaMin<=108 and syphaMin>=96,'Sypha has a useful bounded traversal apex')
    assert(syphaMaxStep<=6,'No doubled integer10/12pixel launch or fall steps')
    assert(r('Player_State')==0 and y==176,'Sypha lands on the same ground')
    local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"passed":true,"seeded_native":true,"apex_y":%d,"max_video_step":%d}\n',syphaMin,syphaMaxStep));f:close();emu.stop(0)
   end
  end
 end
 if frame>2200 then error('Contact diagnostic timed out')end
end,emu.eventType.endFrame)
