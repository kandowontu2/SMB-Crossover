-- Explicit native-enemy admission arena, not a controller route. It tests the
-- legacy stopwatch/ice eligibility contract through the actual AI caller.
-- No CPU registers, PC, ROM or OAM are patched. Invalid dispatch IDs are restored
-- to a real Goomba only AFTER the admission decision, before native JumpEngine.
local frame,depth,index,current=0,0,0,nil
local out=assert(io.open(OUTPUT..ROM_NAME..'-native-freeze-admission.csv','w'))
out:write('case,slot,id,state,stopwatch,iceLo,iceHi,oldTimer,bodyTimer,restoredTimer,force,x,y,aiState\n')
local cases={}
for _,id in ipairs({0,6,0x14,0x15,0x23,0x24,0x2c,0x2d,0x2e,0x35,0xff})do
 for _,state in ipairs({0,2,0x20,0xff})do for effect=0,7 do for _,timer in ipairs({0,7})do for slot=0,5 do
  cases[#cases+1]={id=id,state=state,stop=effect&1,lo=(effect>>1)&1,hi=(effect>>2)&1,timer=timer,slot=slot}
 end end end end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function foreground()return depth==0 and r('CurrentBank')%128==0 end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced freeze-admission interrupts')end,emu.callbackType.exec,pc)end
local returns={}
emu.addMemoryCallback(function()
 if frame<550 or not foreground()then return end
 assert(not current,'Native actor admission is not reentrant')
 index=index+1;current=cases[index]
 if not current then out:close();print('PASS '..#cases..' native actual-caller freeze admissions: all6 slots, state/death, stopwatch,16-bit ice, special-object exclusions, caller timer restore and actual AI movement');emu.stop(0);return end
 local c=current;local cpu=emu.getState();assert(cpu['cpu.x']==c.slot,'Ordinary native actor order reaches all6 slots')
 c.sp=(cpu['cpu.sp']+2)%256
 c.ret=(emu.read(0x100+(cpu['cpu.sp']+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(cpu['cpu.sp']+2)%256,emu.memType.nesDebug)+1)%65536
 c.frozen=(c.state&0x20)==0 and(c.id<0x24 or c.id==0x2d)and(c.stop+c.lo+c.hi>0)
 w('Enemy_ID',c.id,c.slot);w('Enemy_State',c.state,c.slot);w('AvStopwatch',c.stop);w('AvFrozen',c.lo,c.slot);w('AvFrozenHi',c.hi,c.slot);w('TimerControl',c.timer)
 if not returns[c.ret]then returns[c.ret]=true;emu.addMemoryCallback(function()
  if not current or not foreground()or emu.getState()['cpu.sp']~=current.sp then return end
  local q=current;assert(q.body,'Actual native body executed exactly once')
  assert(r('TimerControl')==q.timer,'Actual caller restores preexisting global timer after each actor')
  local expected=(q.timer~=0 or q.frozen)and 0 or 128
  assert(r('Enemy_X_MoveForce',q.slot)==expected,'Actual Goomba AI updates once unless admitted freeze/global timer suspends it: '..index..' got'..r('Enemy_X_MoveForce',q.slot)..' expected'..expected)
  out:write(table.concat({index,q.slot,q.id,q.state,q.stop,q.lo,q.hi,q.timer,q.body,r('TimerControl'),r('Enemy_X_MoveForce',q.slot),r('Enemy_X_Position',q.slot),r('Enemy_Y_Position',q.slot),r('Enemy_State',q.slot)},',')..'\n')
  w('TimerControl',0);w('AvStopwatch',0);w('AvFrozen',0,q.slot);w('AvFrozenHi',0,q.slot);current=nil
 end,emu.callbackType.exec,c.ret)end
end,emu.callbackType.exec,assert(L.RunEnemyObjectsCore))
emu.addMemoryCallback(function()
 if not current or not foreground()then return end
 local c=current;assert(not c.body,'Each admission calls one native actor body')
 local expected=c.frozen and 1 or c.timer
 assert(r('TimerControl')==expected,'Freeze admission preserves actor eligibility and caller timer: '..index)
 assert(r('Enemy_ID',c.slot)==c.id and r('Enemy_State',c.slot)==c.state,'Admission never mutates actor state/identity')
 c.body=expected
 -- A real supported actor runs the remaining native AI; this avoids dispatching
 -- intentionally out-of-range eligibility probes through the native jump table.
 w('Enemy_ID',6,c.slot);w('Enemy_State',0,c.slot)
 w('Enemy_PageLoc',1,c.slot);w('Enemy_X_Position',80+24*c.slot,c.slot);w('Enemy_Y_Position',192,c.slot);w('Enemy_Y_HighPos',1,c.slot)
 w('Enemy_X_Speed',8,c.slot);w('Enemy_Y_Speed',0,c.slot);w('Enemy_X_MoveForce',0,c.slot);w('Enemy_Y_MoveForce',0,c.slot);w('Enemy_MovingDir',1,c.slot);w('Enemy_CollisionBits',0,c.slot);w('Enemy_BoundBoxCtrl',9,c.slot);w('RgEnemyStun',0,c.slot)
end,emu.callbackType.exec,assert(L.RunEnemyObjectsBody))
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240,right=frame==80},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==1 and r('GameEngineSubroutine')==8,'Real menu launches native freeze arena')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('Player_X_Position',8);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',3)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('ScrollLock',1);w('HorizontalScroll',0);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyObjectPageLoc',255)
  w('AvStopwatch',0);w('TimerControl',0);w('InjuryTimer',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0);w('MmDeathFlag',0);w('PlayerOutlinesOff',1)
 end
 assert(frame<3000,'Bounded native freeze admission matrix completes: '..index..'/'..#cases)
end,emu.eventType.endFrame)
