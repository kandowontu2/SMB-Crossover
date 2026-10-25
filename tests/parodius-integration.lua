-- Real menu, then explicitly seeded component arenas. Not a campaign replay.
local wall,t,entered=0,0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
-- Stage complete arena writes at an actual native update boundary. A video
-- callback can otherwise interrupt and mutate an actor halfway through work.
local pending={}
local function w(n,v,i)pending[#pending+1]={assert(L[n],n)+(i or 0),v&255}end
local function shot(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function actual(a)local p=emu.convertAddress(a);assert(p,'Unmapped PRG window');return p.address//8192 end
emu.addMemoryCallback(function()
 if actual(0xa000)~=B.PnNativeFrameReady or not entered then return end
 for _,write in ipairs(pending)do emu.write(write[1],write[2],emu.memType.nesDebug)end
 pending={}
end,emu.callbackType.exec,L.PnNativeFrameReady)
local context;local nmis=0;local kills=0;local peak=0;local logicStart
local budgetChecks,clippedChecks=0,0
local renderTrace={}
local function renderEvent(s)
 renderTrace[#renderTrace+1]=s
 if #renderTrace>60 then table.remove(renderTrace,1)end
end
emu.addMemoryCallback(function()if actual(0xa000)==B.PnDraw and t>=590 then renderEvent('draw t='..t..' used='..r('CurrentOAMOffset'))end end,emu.callbackType.exec,L.PnDraw)
emu.addMemoryCallback(function()
 if actual(0xa000)~=B.RosterProjectileOamReady or not entered or r('GameEngineSubroutine')~=8 then return end
 local p=r('SmPosePtr')+256*r('SmPosePtr',1)
 if r('CurrentOAMOffset')+emu.read(p,emu.memType.nesDebug)>220 then
  local f=assert(io.open(OUTPUT..'render-trace.txt','w'));f:write(table.concat(renderTrace,'\n'));f:close()
 end
 assert(r('CurrentOAMOffset')+emu.read(p,emu.memType.nesDebug)<=220,string.format('Weapon fleet reserves player and world sprites: tick=%d offset=%d ptr=%04x length=%d C=%d pool=%d frame=%d',t,r('CurrentOAMOffset'),p,emu.read(p,emu.memType.nesDebug),emu.convertAddress(0xc000).address//8192,r('PnPool'),r('PnFrame')))
 budgetChecks=budgetChecks+1
end,emu.callbackType.exec,L.RosterProjectileOamReady)
emu.addMemoryCallback(function()
 if actual(0xa000)~=B.MetaspriteRenderLoop or not entered or r('GameEngineSubroutine')~=8 then return end
 local p=r('R0')+256*r('R1')
 if t>=590 then renderEvent(string.format('meta t=%d used=%d ptr=%04x len=%d C=%d body=%04x',t,r('CurrentOAMOffset'),p,emu.read(p,emu.memType.nesDebug),emu.convertAddress(0xc000).address//8192,r('SmPosePtr')+256*r('SmPosePtr',1)))end
 if p~=L.OutlinePoseBuffer then return end
 for i=0,emu.read(p,emu.memType.nesDebug)//4-1 do
  local dy=emu.read(p+3+i*4,emu.memType.nesDebug);if dy>=128 then dy=dy-256 end
  local y=r('R6')+dy
  assert(y>=32 and y<240,'Parodius weapons stay below the status bar without wrapping')
 end
 clippedChecks=clippedChecks+1
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()context={a=actual(0xa000),c=r('CurrentBankC')%128};nmis=nmis+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()assert(context and actual(0xa000)==r('CurrentBank')%128 and actual(0xc000)==context.c,'Interrupt restores bank ownership');context=nil end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()if entered and actual(0xa000)==B.PnWorldContacts then kills=kills+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,name in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','StarInvincibleTimer','GuestHurtTicks','GuestHurtKind','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer'})do w(name,0)end
 w('ScrollLock',1);w('CheatInvincible',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PnX',80);w('PnY',96);w('PnXF',0);w('PnYF',0)
 w('Player_X_Position',72);w('Player_PageLoc',0);w('Player_Y_Position',120);w('Player_Y_HighPos',1)
 for i=1,27 do w('PnActive',0,i);w('PnFrame',0,i);w('PnHitMask',0,i);w('PnContact',0,i)end
 w('GameEngineSubroutine',8);w('OperMode',1)
end
local pulses={[42]=true,[102]=true,[162]=true,[171]=true,[180]=true,[189]=true,[198]=true,[256]=true,[320]=true,[330]=true,[340]=true}
local buys={[222]=true,[237]=true,[252]=true,[267]=true,[282]=true,[297]=true,[457]=true}
for i=0,4 do buys[362+i*15]=true;buys[482+i*18]=true end
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
 else
  b.right=t>=2 and t<22
  b.a=pulses[t]or pulses[t-1]or pulses[t-2]or(t>=600 and t<660 and t%6<3)
  -- Keep a press across several video frames: a native game update can be
  -- skipped while a large source effect is being drawn. Still release fully
  -- between purchases so the original rising-edge rule is exercised.
  b.b=buys[t]or buys[t-1]or buys[t-2]or buys[t-3]or false
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;t=0 end
  if wall>1000 then error('Parodius menu did not enter gameplay')end
  return
 end
 t=t+1
 if t==1 then arena()end
 if t==30 then assert(r('PnX')>=98,'Native one-pixel ship motion');shot('movement')end
 if t==40 then arena();w('Block_Buffer_1',0xc1,103);w('Block_Buffer_1',0x54,104)end
 if t==90 then assert(r('Block_Buffer_1',103)==0xc4,'Shot activates native question block');assert(r('Block_Buffer_1',104)==0x54,'Adjacent protected terrain unchanged')end
 if t==100 then arena();w('Block_Buffer_1',0x54,103)end
 if t==132 then assert(r('Block_Buffer_1',103)==0x54,'Shot preserves ground')end
 if t==150 then
  arena();w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',132);w('Enemy_PageLoc',0);w('Enemy_Y_Position',111);w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',1);w('Enemy_X_Speed',0)
 end
 if t>=150 and t<210 and r('Enemy_Flag')==1 and(r('Enemy_State')&0x20)==0 then w('Enemy_Y_Position',111);w('Enemy_Y_Speed',0)end
 if t==215 then assert(kills>0,'Native projectile defeats real Goomba using SMB bounds')end
 if t==220 then arena();w('VvSpeed',0);w('VvFlags',0);w('VvGun',0);w('VvMeter',1)end
 if t==232 then assert(r('VvSpeed')==1,'Speed cell')end
 if t==235 then w('VvMeter',2)end
 if t==247 then assert((r('VvGun')&8)~=0,'Missile/rocket/potion cell')end
 if t==250 then w('VvMeter',4)end
 if t==263 then assert((r('VvGun')&0xc0)==0x40,'Tailgun/Double cell')end
 if t==264 then shot('tailgun-double')end
 if t==265 then w('VvMeter',8)end
 if t==278 then assert((r('VvGun')&0xc0)==0x80,'Ripple/3-Way/Spread cell')end
 if t==280 then w('VvMeter',16)end
 if t==293 then assert((r('VvGun')&7)==1,'Option cell')end
 if t==295 then w('VvMeter',64)end
 if t==315 then assert(r('PnAux')==15,'Source15-hit shield creation')end
 if t==350 then shot('weapons')end
 for i=0,4 do if t==360+i*15 then w('VvMeter',1)end end
 if t==440 then assert(r('VvSpeed')==4,string.format('Native speed cap4: speed=%d flags=%02x gear=%02x engine=%d death=%d',r('VvSpeed'),r('VvFlags'),r('VvGun'),r('GameEngineSubroutine'),r('MmDeathFlag')))end
 if t==455 then w('VvMeter',32)end
 if t==470 then assert(r('VvGun')==0 and r('VvSpeed')==0,'!? power-down clears equipment')end
 for i=0,4 do if t==480+i*18 then w('VvMeter',16)end end
 if t==580 then assert((r('VvGun')&7)==(PN_VARIANT==1 and 4 or 3),'Native Option cap')end
 if t==590 then w('VvGun',0xa8|(PN_VARIANT==1 and 4 or 3));w('VvFlags',0)end
 if t==600 then logicStart=r('FrameCounter')end
 if t>=600 and t<=660 then local n=0;for i=6,27 do if r('PnActive',i)>0 then n=n+1 end end;peak=math.max(peak,n)end
 if t==665 then assert(peak>=3,string.format('Upgraded weapon fleet fires: peak=%d gear=%02x flags=%02x bells=%02x frame=%d active=%02x',peak,r('VvGun'),r('VvFlags'),r('PnBellFlags'),r('PnFrame'),r('PnActive')));shot('fleet')end
 if t==700 then arena();w('VvGun',0);w('PnBellFlags',2);w('PnBigStage',0);w('PnPhase',0);w('PnSkin',PN_VARIANT)end
 if t==790 then assert(r('PnSkin')==({17,19,20})[PN_VARIANT]and(r('PnBellFlags')&2)~=0,'Original Big transform/skin');shot('big')end
 if t==840 then
  arena();w('VvMeter',0);w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('PowerUpType',0,5);w('InvPickup',0xfc,5);w('InvPickupOwner',0xff,5);w('Enemy_BoundBoxCtrl',3,5)
  w('Enemy_X_Position',72,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',120,5);w('Enemy_Y_HighPos',1,5)
 end
 if t==860 then assert(r('VvMeter')==1 and r('Enemy_Flag',5)==0,'Physical mushroom replacement advances bar without growth')end
 if t==870 then
  w('PnCapActive',1);w('PnCapX',200);w('PnCapPage',0);w('PnCapY',180)
  w('PnCapAge',239)
 end
 if t==878 then assert(r('PnCapActive')==0,'Expired native capsule releases its slot')end
 if t>=3 then assert(r('PnMissing')==0,'No missing native body/weapon pose at component tick '..t)end
 if t==880 then
  assert(budgetChecks>100 and clippedChecks>100,'Renderer assertions exercised actual source fleet frames')
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"variant":%d,"frames":%d,"nmis":%d,"enemyDefeats":%d,"peakProjectiles":%d,"missingPoses":%d,"rendererBudgetChecks":%d,"viewportChecks":%d,"passed":true,"scope":"Controller menu plus explicit movement, block, enemy, equipment, Big and physical-pickup arenas. Not a campaign clear or exact audio/bell parity."}',PN_VARIANT,t,nmis,kills,peak,r('PnMissing'),budgetChecks,clippedChecks));f:close()
  print('PASS native Parodius integration v'..PN_VARIANT);emu.stop(0)
 end
 if wall>4000 then error('Parodius components timed out')end
end,emu.eventType.endFrame)
