-- Explicit native-loop effect arenas. Baseline/optimized builds use the same
-- source equations; no CPU/register/ROM writes. Setup occurs at real pass edges.
local char=assert(LSR_GATE_CHARACTER)
local frame,depth,index,current,preCalls,postCalls=0,0,0,nil,0,0
local cases={{timer=0},{timer=7}}
for field=0,17 do for _,state in ipairs({'live','absent','dead'})do for _,timer in ipairs({0,7})do cases[#cases+1]={field=field,state=state,timer=timer}end end end
if char==4 then cases[#cases+1]={timer=0,deferred=true}end
local out=assert(io.open(OUTPUT..ROM_NAME..'-lsr-effect-gate-canonical.csv','w'))
out:write('case');for i=0,17 do out:write(',effect'..i)end;for i=0,4 do out:write(',frameSnapshot'..i)end;for i=0,5 do out:write(',intervalSnapshot'..i)end;out:write(',hp\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
local names={'RgEnemyStun','MmEnemyFlash','LsrFrozenPose'}
local function get(i)return r(names[i//6+1],i%6)end
local function put(i,v)w(names[i//6+1],v,i%6)end
local function any()for i=0,17 do if get(i)~=0 then return true end end;return false end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced LSR-gate interrupts')end,emu.callbackType.exec,pc)end
emu.addMemoryCallback(function()
 if frame<550 or not bank(0)then return end
 assert(not current,'Complete both effect passes before next arena')
 index=index+1;current=cases[index]
 if not current then out:close();print('PASS '..#cases..' LSR effect-gate arenas c'..char..': zero no-op, every field/slot, paused/live/absent/defeated cleanup, exact effect snapshots'..(char==4 and ', deferred-only fresh sword effect ticks in same update' or''));emu.stop(0);return end
 local c=current;preCalls=0;postCalls=0;c.expected={}
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('LsrIntervalTimer',11,i);if i<5 then w('LsrFrameTimer',17,i)end end
 for i=0,17 do put(i,0);c.expected[i]=0 end
 if c.field then
  local slot=c.field%6;local value=c.field<6 and 12 or c.field<12 and 24 or assert(L.METASPRITE_GOOMBA_WALKING_1)
  put(c.field,value);c.expected[c.field]=value
  if c.state~='absent' then w('Enemy_Flag',1,slot)end
  w('Enemy_ID',6,slot);w('Enemy_State',c.state=='dead' and 0x20 or 0,slot);w('Enemy_PageLoc',1,slot);w('Enemy_X_Position',128,slot);w('Enemy_Y_Position',184,slot);w('Enemy_Y_HighPos',1,slot);w('Enemy_X_Speed',0,slot);w('Enemy_Y_Speed',0,slot);w('Enemy_BoundBoxCtrl',9,slot);w('Enemy_MovingDir',1,slot);w('Enemy_CollisionBits',0,slot);w('AvFrozen',0,slot);w('AvFrozenHi',0,slot)
  if slot<5 then w('EnemyFrameTimer',99,slot)end;w('EnemyIntervalTimer',99,slot)
  if c.timer==0 then if c.state~='live' then c.expected[c.field]=0 elseif c.field>=6 and c.field<12 then c.expected[c.field]=value-1 end end
 end
 w('TimerControl',c.timer);w('RgThrust',0);w('RgAttack',0);w('RgEnemiesPresent',0);w('AvStopwatch',0)
 w('Player_X_Position',8);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_CollisionBits',3)
 for i=0,9 do w('RgShotType',0,i)end
 c.preAny=any()
end,emu.callbackType.exec,assert(L.ProcFireball_Bubble))
emu.addMemoryCallback(function()if current and bank(61)then preCalls=preCalls+1 end end,emu.callbackType.exec,assert(L.LsrEffectsBeforeEnemies))
emu.addMemoryCallback(function()if current and bank(61)then postCalls=postCalls+1 end end,emu.callbackType.exec,assert(L.LsrEffectsAfterEnemies))
emu.addMemoryCallback(function()
 if not current or not bank(59)then return end
 local c=current
 for i=0,17 do assert(get(i)==c.expected[i],'Exact source pre-pass field'..i..' case'..index..': '..get(i)..' expected'..c.expected[i])end
 if L.LsrEffectsAny then assert(preCalls==(c.preAny and 1 or 0),'Only a strict all18-zero pre-pass omits the bank call')else assert(preCalls==1,'Baseline executes original pre-pass')end
end,emu.callbackType.exec,assert(L.InventoryUpdateDrops))
emu.addMemoryCallback(function()
 if not current or not bank(0)then return end
 local c=current
 if c.deferred then
  assert(not any(),'No prior effect can accidentally make the deferred-only gate pass')
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',128);w('Player_PageLoc',1);w('Player_Y_Position',140);w('Player_Rel_YPos',140);w('Player_State',2);w('PlayerStatus',1);w('InvOwnedLo',0,4);w('InvOwnedHi',0,4);w('PlayerFacingDir',1)
  w('RgThrust',1);w('RgThrustReset',1);w('LinkThrustPrev',0);w('LinkThrustNow',0);w('LinkThrustReceipt',0);w('RgEnemiesPresent',1)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',128);w('Enemy_PageLoc',1);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',500%256);w('MmEnemyHealthHi',1)
 end
 c.postAny=any()
end,emu.callbackType.exec,assert(L.GuestPostEnemyCollision))
emu.addMemoryCallback(function()
 if not current or not current.deferred or not bank(8)then return end
 assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==425,'Actual deferred sword alone hits for source75 damage')
 assert(r('RgEnemyStun')==24 and r('MmEnemyFlash')==24,'Actual deferred rectangle creates its source STOP/FLASH')
 current.postAny=true;current.deferredHit=true
end,emu.callbackType.exec,assert(L.LinkDeferredThrustFinish))
emu.addMemoryCallback(function()
 if not current or not bank(0)then return end
 local c=current
 if c.deferred then
  assert(c.deferredHit and r('RgEnemyStun')==23 and r('MmEnemyFlash')==24,'Post gate samples AFTER deferred attack and ticks its new STOP exactly once')
 else
  -- Ryu never creates STOP. A deliberately injected legacy counter still
  -- follows its preexisting movement decrement plus the shared after pass;
  -- preserve that fault-state behavior rather than inventing a Ryu effect.
  if c.field and c.field<6 and c.state=='live' and c.timer==0 then c.expected[c.field]=c.expected[c.field]-(char==10 and 2 or 1)end
  for i=0,17 do assert(get(i)==c.expected[i],'Exact source post-pass field'..i..' case'..index..': '..get(i)..' expected'..c.expected[i])end
 end
 if L.LsrEffectsAny then assert(postCalls==(c.postAny and 1 or 0),'Only a strict all18-zero post-pass omits the bank call')else assert(postCalls==1,'Baseline executes original post-pass')end
 out:write(index);for i=0,17 do out:write(','..get(i))end;for i=0,4 do out:write(','..r('LsrFrameTimer',i))end;for i=0,5 do out:write(','..r('LsrIntervalTimer',i))end;out:write(','..(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi'))..'\n')
 w('TimerControl',0);current=nil
end,emu.callbackType.exec,assert(L.RelativePlayerPosition))
emu.addEventCallback(function()
 local choose=char<6 and frame>=80 and frame<80+20*char and frame%20==0 or char==10 and frame>=100 and frame<180 and frame%20==0
 emu.setInput({start=frame==60 or frame==240,right=choose,down=char==10 and frame==80},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==char and r('GameEngineSubroutine')==8,'Real menu launches LSR zero-effect control')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for _,n in ipairs({'GuestPowerupActive','InjuryTimer','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','XgWall','AvSlash','RgCrouch','CrouchingFlag','StarInvincibleTimer'})do w(n,0)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('ScrollLock',1);w('HorizontalScroll',0);w('EnemyObjectPageLoc',255);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 end
 assert(frame<1500,'Bounded full source effect-gate matrix completes c'..char..' case'..index)
end,emu.eventType.endFrame)
