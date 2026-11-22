-- Controller-only smoke for the newly authored motion component.
-- SONIC_CONFIG is prepended by the strict candidate-specific Python builder.
local C=SONIC_CONFIG
local F,H=C.ram,C.hooks
local frame,polls,mains,motor,pad=0,0,0,0,0
local armed,game,done,finishPending=false,false,false,false
local pending,registered,counts,phases,tail={},{},{},{},{}
local phase,age,active,seenMotor='settle_tap',0,0,0
local jumps,jump,launch,cold={},nil,nil,nil
local jumpEvents,releaseReturns=0,0
local function r(n)return emu.read(assert(F[n],n),emu.memType.nesDebug)end
local function w(at,bank)return emu.read((bank or 2)*8192+(at&8191),emu.memType.nesWorkRam)end
local function signed(at)
 local x=w(at)+256*w(at+1)+65536*w(at+2)
 return x>=8388608 and x-16777216 or x
end
local function mapped(pc)
 local a=emu.convertAddress(pc);if not a then return -1 end
 if a.memType==emu.memType.nesPrgRom then return(a.address//8192)|128 end
 if a.memType==emu.memType.nesWorkRam then return a.address//8192 end
 return -1
end
local function state()
 local top=signed(0xc073)
 return{frame=frame,motor=motor,source_tick=w(0xc092),
  x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),yhigh=r('Player_Y_HighPos'),
  sx=signed(0xc070),sy=top,foot=top+256*w(0xc042),vx=signed(0xc020),vy=signed(0xc060),
  width=w(0xc041),height=w(0xc042),flags=w(0xc030),charge=w(0xc098),previous_pad=w(0xc097),
  input=w(0xc0a8),cue=w(0xc05e),ready=w(0xc119),frame_status=w(0xc116),
  hurt=w(0xc34f),status=r('PlayerStatus'),lives=r('NumberofLives'),
  engine=r('GameEngineSubroutine'),native_state=r('Player_State')}
end
local function json(v)
 if v==nil then return'null'end
 local t=type(v);if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return'"'..v:gsub('[%z\1-\31\\"]',function(c)return string.format('\\u%04x',c:byte())end)..'"'end
 assert(t=='table');local q={}
 if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end
 for k,x in pairs(v)do q[#q+1]=json(tostring(k))..':'..json(x)end
 table.sort(q);return'{'..table.concat(q,',')..'}'
end
local function finish(ok,why)
 if done then return end;done=true;pad=0
 local good,s=pcall(state);if not good then s={snapshot_error=tostring(s)}end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,form=C.form,character=C.name,
  physical_frames=frame,input_polls=polls,Main=mains,accepted_motor=motor,active_samples=active,
  cold=cold,jumps=jumps,launch=launch,post_release_returns=releaseReturns,
  phase_changes=phases,tail=tail,terminal=s,counts=counts,pending=#pending,
  controller_only=true,no_game_actor_inventory_health_seeds=true,files=0,images=0,
  scope='Fresh title/menu identity and constructor, one tap/one held jump, stationary two-press charge/release on real native opening geometry. No fullstage, pickups, interrupts, artwork, audio, cadence or complete Sonic3 fidelity claim.'}))
 emu.stop(ok and 0 or 1)
end
local function guard(name,fn)
 return function(...)
  if done then return end
  local ok,why=pcall(fn,...);if not ok then finish(false,name..': '..tostring(why))end
 end
end
local function count(name)counts[name]=(counts[name]or 0)+1 end
local function bounded(t,v,n)if #t==n then table.remove(t,1)end;t[#t+1]=v end
local function identity()
 return r('SelectedCharacter')==43 and emu.read(0x5ffe,emu.memType.nesDebug)==C.select
end
local function headers()
 for bank=2,3 do
  local q={};for at=0x1fe0,0x1fef do q[#q+1]=string.format('%02x',w(at,bank))end
  assert(table.concat(q)==C.cookie,'Full candidate header bank'..bank)
 end
end
local function auth(name)
 local h=H[name]
 for i=1,#h.hex,2 do
  local kind=h.tag>=128 and emu.memType.nesPrgRom or emu.memType.nesWorkRam
  assert(emu.read(h.offset+(i-1)//2,kind)==tonumber(h.hex:sub(i,i+1),16),'Candidate hook readback '..name)
 end
end
local function grounded(s)return s.flags&128~=0 and s.vy==0 end
local function change(name,s,bits)
 phase=name;age=0;pad=bits
 assert(#phases<16,'Finite motion phases')
 phases[#phases+1]={phase=name,requested=bits,state=s}
end
local function startJump(name,target,s)
 jump={name=name,target_A_updates=target,A_updates=0,minimum_foot=s.foot,baseline_foot=s.foot,
  start=s,events_before=jumpEvents,airborne=false}
 change(name,s,128)
end
local function drive(s)
 if finishPending then return end
 active=active+1;assert(active<=180,'Finite opening motion updates')
 assert(s.ready==1 and s.frame_status==0,'Accepted source frame available')
 assert(s.width==24 and(s.height==24 or s.height==32),'Owned body dimensions')
 assert(s.sx>=32*256 and s.sx<=128*256,'Safe opening position interval')
 assert(s.hurt==0 and s.lives==2 and s.status==0,'No injury or unearned resources')
 if s.cue==1 then jumpEvents=jumpEvents+1 end
 bounded(tail,{phase=phase,requested=pad,state=s},8)
 age=age+1
 if jump then
  if s.input&128~=0 then jump.A_updates=jump.A_updates+1 end
  jump.minimum_foot=math.min(jump.minimum_foot,s.foot)
  if s.flags&128==0 then jump.airborne=true end
  if jump.A_updates>=jump.target_A_updates then pad=0 end
  if jump.airborne and grounded(s)then
   assert(jumpEvents==jump.events_before+1,'One jump impulse per requested press')
   assert(s.sx==jump.start.sx,'Stationary jump retains horizontal position')
   jump.finish=s;jump.height=(jump.baseline_foot-jump.minimum_foot)/256
   jumps[#jumps+1]=jump;local name=jump.name;jump=nil
   if name=='tap'then change('settle_hold',s,0)
   else
    assert(#jumps==2 and jumps[2].height>jumps[1].height+20,'Held jump exceeds tap jump')
    assert(jumps[1].A_updates<jumps[2].A_updates,'Actual accepted tap duration shorter than held')
    change('settle_charge',s,0)
   end
  end
  return
 end
 if phase=='settle_tap'or phase=='settle_hold'or phase=='settle_charge'then
  if not grounded(s)or s.height~=32 or s.input&128~=0 or s.previous_pad&128~=0 then age=0;return end
  assert(s.foot//256==208,'Opening floor foot')
  if age<4 then return end
  if phase=='settle_tap'then startJump('tap',1,s)
  elseif phase=='settle_hold'then startJump('held',20,s)
  else change('charge_down',s,4)end
 elseif phase=='charge_down'then
  if s.input&4~=0 and grounded(s)and s.height==24 then
   assert(s.charge==0 and s.vx==0,'Stationary crouch before charge')
   change('charge_press',s,132)
  end
 elseif phase=='charge_press'then
  if s.charge==1 then change('charge_hold',s,132)end
 elseif phase=='charge_hold'then
  assert(s.charge==1 and s.vx==0 and grounded(s)and s.foot//256==208,'Charge holds position and feet')
  assert(s.sx==cold.sx,'No displacement while charging')
  if age>=6 then change('charge_Aup',s,4)end
 elseif phase=='charge_Aup'then
  if s.input&128==0 then assert(s.charge==1,'Charge survives A release');change('charge_press2',s,132)end
 elseif phase=='charge_press2'then
  if s.charge==2 then change('charge_release',s,0)end
 elseif phase=='charge_release'then
  if s.input&4==0 then
   assert(s.charge==0 and s.vx==1152 and s.height==24 and s.flags&1~=0,'Two-level release launches rolling at4.5px')
   assert(s.sx>cold.sx and grounded(s)and s.foot//256==208,'Launch advances along real floor')
   assert(jumpEvents==2,'Charge presses did not jump')
   launch=s;change('post_release',s,0)
  end
 elseif phase=='post_release'then
  assert(s.charge==0 and s.vx>0 and s.height==24 and s.flags&1~=0,'Released rolling state retained')
  assert(grounded(s)and s.foot//256==208 and jumpEvents==2,'Post-release floor and no additional jump')
  releaseReturns=releaseReturns+1
  if releaseReturns>=3 then finishPending=true;pad=0 end
 else error('Unknown motion phase '..phase)end
end
local function afterMain()
 if not game then return end
 assert(identity()and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'Actual selected ordinary1-1')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaAddrsLOffset')==5,'Authored opening area')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats');headers()
 local s=state()
 if motor>seenMotor then
  seenMotor=motor
  assert(s.x==s.sx//256 and s.y==(s.foot//256-32)&255,'Actual native position projects source feet')
 end
 if finishPending then
  for _,name in ipairs({'GameLoop','SonicHostMain','SonicHostConstruct','OriginalFrame'})do
   assert(counts[name..'_entries']==counts[name..'_returns'],'Balanced '..name)
  end
  assert(counts.SonicHostConstruct_returns==1,'One genuine cold constructor')
  assert(#pending==0 and #jumps==2 and launch,'Complete returned smoke')
  finish(true,'Both jump durations and stationary charge/release returned on native geometry')
 end
end
local function returned(p,c)
 count(p.name..'_returns')
 if p.name=='GameLoop'then mains=mains+1;afterMain()
 elseif p.name=='OriginalFrame'then
  if c['cpu.ps']&1~=0 then motor=motor+1;if game then drive(state())end
  else count('OriginalFrame_C0')end
 end
end
local function settle()
 local c=emu.getState();local pc,sp=c['cpu.pc'],c['cpu.sp']
 while #pending>0 do
  local p=pending[#pending]
  if p.pc~=pc or p.sp~=sp or p.tag~=mapped(pc)then return end
  table.remove(pending);returned(p,c)
 end
end
local function register(pc)
 if registered[pc]then return end;registered[pc]=true
 emu.addMemoryCallback(guard('Matched actual return',settle),emu.callbackType.exec,pc)
end
local function enter(name)
 local h=H[name]
 if mapped(h.pc)~=h.tag then return end
 if name~='GameLoop'and(not armed or not identity())then return end
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 count(name..'_entries');pending[#pending+1]={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}
 register(pc)
end
local function pause(n)for _=1,n do coroutine.yield()end end
local function press(bits)pad=bits;pause(4);pad=0;pause(8)end
local function wait(fn)
 for _=1,1200 do if fn()then return end;coroutine.yield()end
 error('Natural title/menu/gameplay bound')
end
local boot=coroutine.create(function()
 wait(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Natural initial menu slot0')
 for _,bits in ipairs({4,4,4,1})do press(bits)end
 assert(r('CrossoverMenuIndex')==25 and emu.read(0x5ffe,emu.memType.nesDebug)==0,'Natural MrGimmick slot25')
 for _=1,C.select do press(32)end;assert(identity(),'Actual selected Sonic form')
 armed=true;press(16)
 wait(function()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
  and w(0xc119)==1 and w(0xc041)==24 and w(0xc042)==32 and w(0xc030)&128~=0
  and(counts.SonicHostConstruct_returns or 0)>=1 and(counts.OriginalFrame_returns or 0)>=1 end)
 for name in pairs(H)do auth(name)end;headers()
 assert(counts.SonicHostConstruct_entries==1 and counts.SonicHostConstruct_returns==1,'Actual returned cold constructor')
 cold=state();assert(cold.x==40 and cold.sx==40*256 and cold.lives==2 and cold.charge==0,'Fresh native origin/resources/charge')
 assert(cold.width==24 and cold.height==32,'Fresh owned standing body')
 game=true;seenMotor=motor;pad=0
 while not done do coroutine.yield()end
end)
guard('Setup',function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact private motion candidate')
 assert(C.select==3 or C.select==4,'Sonic or Super Sonic only')
 for name,h in pairs(H)do
  emu.addMemoryCallback(guard(name,function()enter(name)end),emu.callbackType.exec,h.pc)
 end
 emu.addEventCallback(guard('Physical input poll',function()
  polls=polls+1
  emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,
   start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
 end),emu.eventType.inputPolled)
 emu.addEventCallback(guard('Physical frame',function()
  frame=frame+1;assert(frame<=6000,'Bounded physical motion frames')
  local ok,why=coroutine.resume(boot);assert(ok,why)
 end),emu.eventType.endFrame)
end)()
