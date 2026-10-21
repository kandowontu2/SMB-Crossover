-- Isolated real helper-call arenas, distinct from whole injury/motion cases.
-- Only RAM inputs are authored at actual routine entries. CPU/ROM/PC/registers
-- are never patched. Test strict Q16 distance/equality, timer fallback, source
-- side/ceiling rules and caller ABI independently of terrain timing.
local cases={}
for _,dir in ipairs({1,2})do
 for _,delta in ipairs({-65536,-1,0,1,65536})do for _,ticks in ipairs({1,2,72})do
  cases[#cases+1]={fn='LsrHurtTick',dir=dir,delta=delta,ticks=ticks}
 end end
end
for _,char in ipairs({4,5,10})do for _,dir in ipairs({1,2})do
 for _,side in ipairs({'none','opposite','matching'})do
  cases[#cases+1]={fn='LsrHurtAfterCollision',char=char,dir=dir,side=side}
 end
 for _,jumped in ipairs({false,true})do
  cases[#cases+1]={fn='LsrHurtAfterCollision',char=char,dir=dir,side='none',ceiling=true,jumped=jumped}
 end
 if char~=4 then cases[#cases+1]={fn='LsrHurtAfterCollision',char=char,dir=dir,side='none',ground=true}end
end end
local frame,index,depth,checks=0,1,0,0
local pending,returns={},{ }
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function setq(n,v)local a=math.floor(v*65536+.5)%0x1000000;for i=0,2 do w(n,(a>>(8*i))&255,i)end end
local function xq()return r('MmXFraction')+256*r('MmXFraction',1)+65536*r('Player_X_Position')+16777216*r('Player_PageLoc')end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced endpoint-fixture interrupts')end,emu.callbackType.exec,pc)end
for _,fn in ipairs({'LsrHurtTick','LsrHurtAfterCollision'})do
 emu.addMemoryCallback(function()
  if frame<550 or depth~=0 or r('CurrentBank')%128~=61 or pending.c then return end
  local c=cases[index];if not c or c.fn~=fn then return end
  local s=emu.getState();local sp=s['cpu.sp']
  local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  pending={c=c,sp=sp,x=s['cpu.x'],y=s['cpu.y'],offset=r('ObjectOffset')}
  w('SelectedCharacter',c.char or 4);w('GuestHurtKind',c.char or 4);w('GuestHurtTicks',c.ticks or 1);w('LsrHurtFlags',c.dir+(c.jumped and 8 or 0))
  if fn=='LsrHurtTick'then
   local endpoint=384*65536+0x80ff;local pos=endpoint+c.delta
   for i=0,3 do w('LsrHurtEndX',(endpoint>>(8*i))&255,i)end
   w('MmXFraction',pos&255);w('MmXFraction',(pos>>8)&255,1);w('Player_X_Position',(pos>>16)&255);w('Player_PageLoc',(pos>>24)&255)
   local overshoot=c.dir==1 and c.delta>0 or c.dir==2 and c.delta<0
   pending.ended=c.ticks==1 or overshoot;pending.position=c.ticks~=1 and overshoot and endpoint or pos
  else
   w('Player_State',c.ground and 0 or 2);w('Player_Y_Speed',c.ceiling and 1 or 0xfe);setq('MmVY',-2);setq('MmVX',c.dir==1 and 1.25 or-1.25)
   w('Player_CollisionBits',c.side=='matching'and(255~c.dir)or c.side=='opposite'and(255~(c.dir~3))or 255)
   w('AvSlash',1);w('AvFlip',1);w('Square1SoundQueue',0)
   pending.ended=c.char==4 and c.side=='matching'or c.char~=4 and c.ground==true
   pending.vx=c.side=='matching'and 0 or(c.dir==1 and 1.25 or-1.25)
   pending.vy=c.ceiling and c.jumped and 100/120 or-2
  end
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if not pending.c or depth~=0 then return end
    local s=emu.getState();if s['cpu.sp']~=(pending.sp+2)%256 then return end
    local c=pending.c
    assert(s['cpu.x']==pending.x and s['cpu.y']==pending.y and r('ObjectOffset')==pending.offset,'Source endpoint/contact helper preserves caller X/Y/ObjectOffset')
    assert(s['cpu.ps']&1==(pending.ended and 1 or 0),'Source strict distance/fallback/side/landing return carry case'..index)
    if c.fn=='LsrHurtTick'then
     assert(xq()==pending.position and r('GuestHurtTicks')==c.ticks-1,'Strict endpoint clamps only overshoot; fallback/equality preserve source position')
    else
     assert(math.abs(q('MmVX')-pending.vx)<.00003 and math.abs(q('MmVY')-pending.vy)<.00003,'Exact source side stop and jumped-only100/120 ceiling response')
     if c.ceiling then assert(r('Square1SoundQueue')&2~=0,'Actual source ceiling receipt queues hit-ceiling cue')end
     if c.char==10 and c.ground then assert(r('AvSlash')==0 and r('AvAudioRequest')==24,'Ryu landing clears Jump Slash and requests source landing cue')end
    end
    checks=checks+1;pending={};index=index+1
    w('SelectedCharacter',4);w('GuestHurtKind',4);w('GuestHurtTicks',72);w('GuestInvulTicks',0);w('LsrHurtFlags',1)
    for i=0,3 do w('LsrHurtEndX',255,i)end
    if not cases[index]then print('PASS '..checks..' exact source Q16 endpoint/equality/fallback and contact-return arenas, both directions/three characters, source ceiling/SFX and X/Y/ObjectOffset ABI');emu.stop(0)end
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,assert(L[fn]))
end
emu.addEventCallback(function()emu.setInput({start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 for i=0,5 do w('Enemy_Flag',0,i)end
 if not pending.c then
  w('SelectedCharacter',4);w('GuestHurtKind',4);w('GuestHurtTicks',72);w('GuestHurtVisible',1);w('GuestPowerupActive',0);w('GameEngineSubroutine',8);w('TimerControl',0)
  w('Player_X_Position',128);w('Player_PageLoc',1);w('Player_Y_Position',96);w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',0);w('ScrollLock',1)
  for i=0,3 do w('LsrHurtEndX',255,i)end
 end
 assert(frame<1500,'Bounded source endpoint/contact helper matrix completes')
end,emu.eventType.endFrame)
