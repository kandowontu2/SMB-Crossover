-- Real profile-call arenas. Source Link keeps15NESpx. Simon/Ryu hurt is25px;
-- Simon's source Start forces air, and real collision queries precede landing
-- recovery. Its grounded locked state is not an artificial test requirement.
local cases={}
for _,fn in ipairs({'MegaManCollisionBox','MegaManCollisionAdder'})do for _,char in ipairs({4,5,10})do
 for _,hurt in ipairs({false,true})do for _,state in ipairs({0,1})do for _,dir in ipairs({1,2})do
  if not(char==5 and hurt and state==0)then cases[#cases+1]={fn=fn,char=char,hurt=hurt,state=state,dir=dir}end
 end end end
end end
local frame,index,depth,checked=0,1,0,0
local pending,returns={},{ }
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function w(n,v)emu.write(assert(L[n],n),v,emu.memType.nesDebug)end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced hurt profile interrupts')end,emu.callbackType.exec,pc)end
for _,fn in ipairs({'MegaManCollisionBox','MegaManCollisionAdder'})do
 emu.addMemoryCallback(function()
  if frame<550 or depth~=0 or pending.c then return end
  local c=cases[index];if not c or c.fn~=fn then return end
  local s=emu.getState();local sp=s['cpu.sp']
  local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  pending={c=c,sp=sp,x=s['cpu.x'],offset=r('ObjectOffset')}
  w('SelectedCharacter',c.char);w('GuestHurtKind',0);w('GuestHurtTicks',c.hurt and 1 or 0);w('Player_State',c.state);w('PlayerFacingDir',c.dir);w('RgCrouch',0);w('CrouchingFlag',0);w('PlayerSize',0);w('MmSliding',0)
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if not pending.c or depth~=0 then return end
    local s=emu.getState();if s['cpu.sp']~=(pending.sp+2)%256 then return end
    local c=pending.c;local shortHead=c.hurt or(c.char==5 and c.state~=0)
    local wanted=c.fn=='MegaManCollisionBox'and(c.char==4 and 18 or c.hurt and 16 or 15)or(c.char==4 and 9 or shortHead and 7 or 6)
    assert(s['cpu.y']==wanted and s['cpu.x']==pending.x and r('ObjectOffset')==pending.offset,'Real hurt/normal profile returns exact source Y and preserves X/ObjectOffset: '..c.fn..' c'..c.char..' hurt'..tostring(c.hurt)..' state'..c.state..' dir'..c.dir..' Y'..s['cpu.y']..' expected'..wanted..' X'..s['cpu.x']..'/'..pending.x..' ObjectOffset'..r('ObjectOffset')..'/'..pending.offset)
    if c.fn=='MegaManCollisionBox'then
     local top=emu.read(L.BoundBoxCtrlData+4*wanted+1,emu.memType.nesDebug)
     local bottom=emu.read(L.BoundBoxCtrlData+4*wanted+3,emu.memType.nesDebug)
     assert(top==(c.char==4 and 17 or c.hurt and 7 or 1)and bottom==32,'Actual decoded body height is source15/25 or retained normal31')
    else
     local offset=emu.read(L.BlockBufferAdderData+wanted,emu.memType.nesDebug)
     assert(emu.read(L.BlockBuffer_Y_Adder+offset,emu.memType.nesDebug)==(c.char==4 and 17 or shortHead and 7 or 1),'Actual BG head probe matches source hurt top or retained normal profile')
    end
    checked=checked+1;index=index+1;pending={};w('GuestHurtTicks',0)
    if not cases[index]then print('PASS '..checked..' LSR real hurt/normal body/head profile calls: Link15 and Simon/Ryu25NESpx, both directions and reachable lifecycle states');emu.stop(0)end
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,assert(L[fn]))
end
emu.addEventCallback(function()emu.setInput({start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;assert(frame<1600,'Bounded LSR hurt profile query matrix completes')end,emu.eventType.endFrame)
