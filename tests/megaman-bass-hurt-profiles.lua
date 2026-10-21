-- Isolated profile-call fixture, not level progress. Raw2.02 frame14 takeDamage
-- keeps stand's48Flashpx HRect; jump frame15 alone changes to55Flashpx.
-- Author only profile inputs at real routine entries and observe their returns.
local frame,index=0,1
local cases={}
for _,fn in ipairs({'MegaManCollisionBox','MegaManCollisionAdder'})do
 for _,char in ipairs({1,9})do for _,hurt in ipairs({false,true})do
  for _,state in ipairs({0,1})do for _,dir in ipairs({1,2})do
   cases[#cases+1]={fn=fn,char=char,hurt=hurt,state=state,dir=dir}
  end end
 end end
end
local pending,returns={},{ }
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function w(n,v)emu.write(assert(L[n],n),v,emu.memType.nesDebug)end
for _,fn in ipairs({'MegaManCollisionBox','MegaManCollisionAdder'})do
 emu.addMemoryCallback(function()
  if frame<550 or pending.c then return end
  local c=cases[index];if not c or c.fn~=fn then return end
  local s=emu.getState();local sp=s['cpu.sp']
  local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
  if not returns[fn]then
   returns[fn]=pc
   emu.addMemoryCallback(function()
    if not pending.c or pending.c.fn~=fn or emu.getState()['cpu.sp']~=pending.sp+2 then return end
    local p=pending.c
    local airborne=p.char==1 and p.state~=0 and not p.hurt
    local expected=(fn=='MegaManCollisionBox'and 12 or 3)+(airborne and 1 or 0)
    local actual=emu.getState()['cpu.y']
    assert(actual==expected,'Source48px hurt profile '..fn..' char'..p.char..' state'..p.state..' hurt'..tostring(p.hurt)..' direction'..p.dir..' actual'..actual..' expected'..expected)
    if fn=='MegaManCollisionBox'then
     local top=emu.read(L.BoundBoxCtrlData+actual*4+1,emu.memType.nesDebug)
     local bottom=emu.read(L.BoundBoxCtrlData+actual*4+3,emu.memType.nesDebug)
     assert(top==(airborne and 4 or 8) and bottom==32,'Decoded body bounds match source hurt24NESpx or the normal pose')
    else
     local offset=emu.read(L.BlockBufferAdderData+actual,emu.memType.nesDebug)
     assert(emu.read(L.BlockBuffer_Y_Adder+offset,emu.memType.nesDebug)==(airborne and 4 or 8),'The actual background head probe uses the source hurt head extent')
    end
    w('GuestHurtTicks',0);pending={};index=index+1
    if not cases[index]then print('PASS 32 source MM/Bass hurt/normal ground/air body/background profiles, both directions');emu.stop(0)end
   end,emu.callbackType.exec,pc)
  end
  assert(returns[fn]==pc,'Each real profile caller is stable')
  pending={c=c,sp=sp}
  w('SelectedCharacter',c.char);w('GuestHurtKind',0);w('GuestHurtTicks',c.hurt and 13 or 0)
  w('Player_State',c.state);w('PlayerFacingDir',c.dir);w('MmSliding',0);w('RgCrouch',0);w('CrouchingFlag',0);w('PlayerSize',0)
 end,emu.callbackType.exec,assert(L[fn]))
end
emu.addEventCallback(function()emu.setInput({right=frame==80,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;assert(frame<1000,'Bounded source profile matrix completes')end,emu.eventType.endFrame)
