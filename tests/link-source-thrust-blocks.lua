-- Separate isolated block arenas exercise2.02 attackObjPiercing/nonPiercing:
-- real attackable contact, continuous C/L receipt, separation, and terrain.
local frame,depth,index,pending=0,0,1,false
local commit=nil
local cases={}
for power=0,2 do for direction=1,2 do
 for _,kind in ipairs({'first','continuous','separated','recontact','terrain','real-brick'})do
  cases[#cases+1]={power=power,direction=direction,kind=kind}
 end
end end
local hp=250
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function raw(n)local q=r(n)+256*r(n,1)+65536*r(n,2);return q>=0x800000 and q-0x1000000 or q end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link block fixture interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()
 local c=frame>=550 and cases[index]or nil
 emu.setInput({right=frame>=80 and frame<160 and(frame-80)%20==0,start=frame==200,down=c and c.direction==1,up=c and c.direction==2},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or pending or depth~=0 or r('CurrentBank')%128~=22 then return end
 local c=cases[index];local mask=c.direction==1 and 4 or 8
 if (r('SavedJoypadBits')&12)~=mask then return end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i)end
 w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',c.direction==1 and 120 or 111);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('GameEngineSubroutine',8);w('AreaType',1);w('SwimmingFlag',0);w('TimerControl',0);w('GuestPowerupActive',0)
 w('Player_State',1);w('PlayerStatus',c.power);w('PlayerSize',0);w('InvOwnedLo',0,4);w('InvOwnedHi',0,4)
 w('Player_X_Speed',0);w('Player_Y_Speed',c.direction==2 and 255 or 0);w('Player_CollisionBits',255);w('InjuryTimer',0)
 w('RgAttack',0);w('RgCrouch',0);w('CrouchingFlag',0);w('RgThrustReset',c.direction)
 w('NoiseSoundQueue',0);w('Square1SoundQueue',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 if c.direction==2 then w('MmVY',255,2)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end;w('MmFrictionYActive',0)
 if c.kind=='first' or c.kind=='terrain' or c.kind=='real-brick'then
  for i=0,15 do w('RgMeleeBlocks',255,i)end
  hp=c.kind=='real-brick'and 34 or 250
 end
 local row=c.direction==1 and 128 or 64;c.cell=row+8
 w('MmBrickHealth',hp,c.cell)
 if c.kind~='separated'then
  w('Block_Buffer_1',c.kind=='terrain'and 0x54 or 0x51,c.cell)
  if c.kind=='terrain'then w('MmSolidTerrain',1,c.cell)end
 end
 pending=true
end,emu.callbackType.exec,assert(L.RosterMovement))
emu.addMemoryCallback(function()
 if not pending or commit or depth~=0 or r('CurrentBank')%128~=8 then return end
 local c=cases[index];local hit=c.kind=='first'or c.kind=='recontact'or c.kind=='real-brick'
 local expected=hit and math.max(0,hp-({50,75,100})[c.power+1])or hp
 if c.kind~='real-brick'then assert(r('MmBrickHealth',c.cell)==expected,'Link source attackable/separated block receipt '..c.kind..' power'..c.power..' dir'..c.direction..': '..r('MmBrickHealth',c.cell)..' expected'..expected)end
 local vy=raw('MmVY')/65536
 if hit then
  assert(math.abs(vy-(c.direction==1 and -325/120 or 0))<.00002,'Down attackable block bounce / Up upward cancel '..c.kind)
 elseif c.direction==1 then assert(vy>=0,'Unattackable/continuous terrain cannot invent another Down bounce')
 else assert(vy<0,'Unattackable/continuous terrain cannot cancel another Up movement')end
 if c.kind=='real-brick'then
  -- Native BrickShatter installs the$23 collision sentinel and debris first;
  -- BlockObjMT_Updater commits blank only when its VRAM queue is available.
  local shatter=false
  for slot=0,1 do if(r('Block_State',slot)&15)==2 and r('Block_RepFlag',slot)~=0 and r('Block_Metatile',slot)==0 then shatter=true end end
  assert(r('Block_Buffer_1',c.cell)==0x23 and shatter,'Real34-health brick dispatches native shatter/debris before deferred blank commit')
  assert(r('NoiseSoundQueue')~=0,'Real brick shatter queues native sound')
 end
 assert(r('RgThrustReset')==c.direction,'Thrust has held-direction state, not an18-update bounce lockout')
 hp=expected
 if c.kind=='real-brick'then commit={c=c,updates=0};return end
 pending=false;index=index+1
 if not cases[index]then print('PASS '..#cases..' Link source thrust block contacts, C/L separation, terrain rejection, bounce/cancel and real shatter SFX');emu.stop(0)end
end,emu.callbackType.exec,assert(L.RosterWeaponsFinish))
emu.addMemoryCallback(function()
 if not commit or depth~=0 then return end
 assert(emu.read(L.NoDecTimers,emu.memType.nesDebug)==0xe6 and emu.read(L.NoDecTimers+1,emu.memType.nesDebug)==L.FrameCounter,'Actual completed-update brick commit boundary')
 commit.updates=commit.updates+1
 if r('Block_Buffer_1',commit.c.cell)==0 then
  commit=nil;pending=false;index=index+1
  if not cases[index]then print('PASS '..#cases..' Link source thrust block contacts, C/L separation, terrain rejection, bounce/cancel, debris, bounded blank commit and real shatter SFX');emu.stop(0)end
 else assert(commit.updates<=12,'Native shatter blank commits within12 completed updates')end
end,emu.callbackType.exec,assert(L.NoDecTimers))
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==4,'Real menu launches Link before block arenas')end
 assert(frame<1400,'All real block contact cases finish')
end,emu.eventType.endFrame)
