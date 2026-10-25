-- Explicitly seeded performance arenas. Gear is supplied, not collected.
-- No hardware timing bypass, injected animation or disabled sprite limit.
local wall,entered,t,updates=0,false,0,0
local phaseIndex,phaseStart,armed=0,0,true
local phases={'idle','enemies','normal-fire','full-fleet'}
PERF_PHASE='startup'
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local profile=(function() PERFORMANCE_OBSERVER end)()({out=OUTPUT,phase=function()return PERF_PHASE end})
local peaks={};local samples={}
local inputs=assert(io.open(OUTPUT..'performance-native-inputs.csv','w'))
inputs:write('phase,update,held,fresh\n')
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for i=176,207 do w('Block_Buffer_1',0x54,page*208+i)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=1,27 do w('PnActive',0,i);w('PnFrame',0,i);w('PnContact',0,i);w('PnHitMask',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','InjuryTimer','StarInvincibleTimer'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PnX',80);w('PnY',96);w('PnXF',0);w('PnYF',0);w('PnAux',0)
 w('VvGun',phaseIndex==4 and(0xa8|(PN_VARIANT==1 and 4 or 3))or 0);w('VvFlags',0);w('VvSpeed',0)
 w('PnBellFlags',0);w('VvMeter',0);w('VvHurt',0)
 if phaseIndex>=2 then
  for i=0,1 do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i)
   w('Enemy_X_Position',160+i*64,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',192,i);w('Enemy_Y_HighPos',1,i)
   w('Enemy_X_Speed',0xf8,i);w('Enemy_Y_Speed',0,i);w('Enemy_MovingDir',2,i)
  end
 end
end
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=B.PnNativeFrameReady then return end
 if armed then
  phaseIndex=phaseIndex+1;assert(phases[phaseIndex]);PERF_PHASE=phases[phaseIndex]
  phaseStart=updates;arena();armed=false
 end
 inputs:write(table.concat({PERF_PHASE,updates-phaseStart,r('VvHeld'),r('VvFresh')},',')..'\n')
 updates=updates+1
end,emu.callbackType.exec,L.PnNativeFrameReady)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
 elseif phaseIndex>=3 then b.a=(updates-phaseStart)%6<3 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true end
  assert(wall<1400,'Cold Parodius entry');return
 end
 t=t+1
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Performance arena stays live')
 if phaseIndex>0 then
  local active=0;for i=6,27 do if r('PnActive',i)>=128 then active=active+1 end end
  peaks[PERF_PHASE]=math.max(peaks[PERF_PHASE]or 0,active);samples[PERF_PHASE]=(samples[PERF_PHASE]or 0)+1
  if updates-phaseStart>=120 then
   if phaseIndex==#phases then
    assert((peaks['normal-fire']or 0)>0 and(peaks['full-fleet']or 0)>=3,'Both ordinary fire and a full native fleet actually run')
    profile.finish()
    inputs:close()
    local f=assert(io.open(OUTPUT..'performance-proof.json','w'));f:write('{"passed":true,"variant":'..PN_VARIANT..',"nativeUpdates":'..updates..',"videoFrames":'..t..',"normalShotPeak":'..peaks['normal-fire']..',"fleetPeak":'..peaks['full-fleet']..',"scope":"Cold menu then explicit idle/live-enemy/ordinary-shot/full-fleet performance arenas; no pickup or campaign certificate"}');f:close()
    print('PASS four bounded native performance arenas');emu.stop(0)
   else armed=true end
  end
 end
 assert(t<4000,'Bounded native update progress')
end,emu.eventType.endFrame)
