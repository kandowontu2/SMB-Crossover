assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Pinned Arthur nightly')
local input,frame,updates,moves,steps={},0,0,0,0
local phase,at='wound',0
local opening=CPU_CONTROLLER_OPENING and 'play' or 'title'
local menuPulse,pulseFrames=nil,0
local pending,events,heads,births,collections={},{},{},{},{}
local damage,pickup,after,latest,initial,mature
local seenHooks={}
local jumpStep,attempts=nil,0
local lastUpdate=-1
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function x()return pos('Player_X_Position','Player_PageLoc')end
local function score()local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n end
local function state()
 return{x=x(),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),engine=r('GameEngineSubroutine'),
  lives=r('NumberofLives'),status=r('PlayerStatus'),flags=r('ArR_04F0'),weapon=r('ArR_053A'),
  ready=r('ArHostReady'),mode=r('ArMode'),jumps=r('ArJumpCount'),last=r('ArLastPickup'),
  update=updates,moves=moves,steps=steps,frame=frame,score=score(),injury=r('InjuryTimer')}
end
local function actor(i)
 return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i),
  kind=r('PowerUpType',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}
end
local function mapped(pc)
 local q=emu.convertAddress(pc);return q and q.memType,q and q.address
end
local function valid(h)
 local mem,offset=mapped(h.pc)
 if mem~=(h.tag>=128 and emu.memType.nesPrgRom or emu.memType.nesWorkRam)or offset~=h.offset then return false end
 for i,v in ipairs(h.bytes)do if emu.read(h.pc+i-1,emu.memType.nesDebug)~=v then error('Changed actual Arthur hook '..h.name)end end
 return true
end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local a={}
 if #v>0 then for _,q in ipairs(v)do a[#a+1]=json(q)end;return'['..table.concat(a,',')..']'end
 for k,q in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(q)end
 table.sort(a);return'{'..table.concat(a,',')..'}'
end
local done=false
local function finish(ok,why)
 if done then return end;done=true
 local q={passed=ok,reason=why,ROM_SHA256=C.sha,controller_only=true,game_state_writes=false,files=0,images=0,
  physical_frames=frame,Main=updates,movement_returns=moves,original_steps=steps,initial=initial,
  damage=damage,pickup=pickup,after=after,terminal=state(),events=events,heads=heads,births=births,
  collections=collections,mature=mature,latest=latest,seen_hooks=seenHooks,phase=phase,pending_returns=#pending}
 print('SMB_NATIVE_RECEIPT '..json(q));emu.stop(ok and 0 or 1)
end
local function guarded(fn)
 return function(...)
  if done then return end
  local ok,why=pcall(fn,...)
  if not ok then finish(false,tostring(why):match('[^\r\n]+') or 'Arthur observer error')end
 end
end
local function mark(p)
 phase=p;at=steps;assert(#events<32,'Bounded Arthur phases')
 events[#events+1]={phase=p,player=state()}
end
local function steer(target,n)
 return{right=x()<target-n,left=x()>target+n}
end
local function released()return r('A_B_Buttons')&128==0 and r('PreviousA_B_Buttons')&128==0 end
local function item()
 for i=0,5 do local q=actor(i);if q.flag>0 and q.id==46 then return q end end
end
local function policy()
 local s=state();latest={player=s,item=item()}
 assert(s.lives==2 and s.high==1 and s.engine~=11,'Living Arthur pickup route')
 assert(s.ready==167 and r('SelectedCharacter')==32,'Actual initialized Arthur owner')
 assert(updates<1900,'Bounded natural Arthur Mushroom route')
 if phase=='wound'then
  if not damage then return{right=x()<240}end
  assert(s.flags&32~=0,'Original hit removes armor before Mushroom choice')
  if s.mode~=0 then return{}end
  if s.flags&0x40~=0 then return{right=s.x<322,b=steps%14<3}end
  mark('align')
 end
 if phase=='align'then
  if s.mode~=0 then return{}end
  if math.abs(s.x-329)<=2 and r('Player_X_Speed')==0 and released()then
   attempts=attempts+1;assert(attempts<=4,'Bounded actual first-block head attempts')
   jumpStep=steps;mark('head');return{a=true}
  end
  return steer(329,2)
 end
 if phase=='head'then
  if item()then mark('collect')end
  if phase=='head'then
   local age=steps-jumpStep
   if age>60 and s.mode==0 then mark('align');return{}end
   return{a=age<4 or(age>=12 and age<18)}
  end
 end
 if phase=='collect'then
  if pickup then input={};return{}end
  local a=item()
  assert(steps-at<480,'Bounded naturally moving Mushroom contact')
  if a then
   assert(a.kind==0,'Real naked Arthur block emits Mushroom')
   if a.y<148 then return steer(396,2)end
   return steer(a.x-3,3)
  end
  return{}
 end
 if phase=='retain'then return{right=x()<430}end
 return{}
end
local function returned(p)
 local s=state()
 if p.name=='Movement'then
  moves=moves+1
  if pickup and phase=='retain'and moves>=pickup.after.moves+25 and s.mode==0 then
   assert(s.flags&32==0 and s.status==1 and s.weapon==initial.weapon and s.last==5,'Original restored armor persists')
   assert(score()>=pickup.before.score+1000,'Actual pickup score persists')
   after=state();assert(#pending==0,'Arthur owning workers unwound');finish(true,'Natural Mushroom restored Arthur armor and retained25movement returns')
  end
 elseif p.name=='TakeHit'then
  if p.before.flags&32==0 and s.flags&32~=0 then
   assert(not damage and p.target.flag==1 and p.target.id==6,'Single real first Goomba armor loss')
   damage={before=p.before,after=s,target=p.target,return_pc=p.pc}
  end
 elseif p.name=='SourcePickup'then
  collections[#collections+1]={value=p.value,before=p.before,after=s}
  if p.value==5 then
   assert(damage and #births>0 and #heads>0 and mature,'Real injury, authored head bump and mature item precede restoration')
   assert(p.before.flags&32~=0 and s.flags&32==0 and s.last==5,'Original armor event5 executes')
   pickup={before=p.before,after=s,event=p.value};mark('retain')
  end
 end
end
local function settle()
 local cpu=emu.getState();local pc,sp=cpu['cpu.pc'],cpu['cpu.sp']
 while #pending>0 do
  local p=pending[#pending]
  if p.pc~=pc or p.sp~=sp then break end
  local mem,offset=mapped(pc)
  if mem~=p.mem or offset~=p.offset then break end
  table.remove(pending);returned(p)
 end
end
local function enter(name,h)
 if not valid(h)or r('SelectedCharacter')~=32 then return end
 seenHooks[name]=(seenHooks[name]or 0)+1
 if name=='Step'then steps=steps+1;return end
 if name=='GameLoop'then updates=updates+1;return end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local pc=1+emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)
 pc=pc&65535
 local mem,offset=mapped(pc)
 local p={name=name,pc=pc,sp=(sp+2)&255,mem=mem,offset=offset,before=state()}
 p.before.score=score()
 if name=='TakeHit'then p.target=actor(r('ObjectOffset'))
 elseif name=='SourcePickup'then p.value=cpu['cpu.a']
 elseif name=='Head'then
  if x()<400 and #heads<8 then heads[#heads+1]={player=state(),row=r('R2'),pointer=r('R6')+256*r('R7'),tile=cpu['cpu.a']}end
  return
 end
 assert(#pending<12,'Bounded actual Arthur return stack');pending[#pending+1]=p
end
local guardedSettle=guarded(settle)
emu.addMemoryCallback(function(address)
 local top=pending[#pending]
 if top and (address==nil or address==top.pc)then guardedSettle()end
end,emu.callbackType.exec,0x100,0xffff)
for name,h in pairs(C.hooks)do
 emu.addMemoryCallback(guarded(function()enter(name,h)end),emu.callbackType.exec,h.pc)
end
local seenBirth={}
local function observe()
 local a=item()
 if a and not seenBirth[a.slot]then
  assert(a.kind==0 and damage and #heads>0,'Authored first naked Mushroom birth')
  seenBirth[a.slot]=true;births[#births+1]={actor=a,player=state()}
 end
 if a and a.state&128~=0 and not mature then mature={actor=a,player=state()}end
end
local function pulse(key)
 if pulseFrames<5 then input={[key]=true}else input={}end
 pulseFrames=pulseFrames+1
 if pulseFrames>=14 then pulseFrames=0;return true end
end
local function menu()
 if opening=='title'then
  if frame<70 then input={};return end
  if r('CrossoverMenuState')~=2 then pulse('start');return end
  opening='menu';pulseFrames=0
 end
 if opening=='menu'then
  local index=r('CrossoverMenuIndex')
  if index~=31 then pulse(index<24 and 'up' or 'left');return end
  assert(r('SelectedCharacter')==32,'Arthur original menu identity')
  opening='start';pulseFrames=0
 end
 if opening=='start'then
  if r('OperMode')==1 then opening='wait';input={};return end
  pulse('start');return
 end
 input={}
end
emu.addEventCallback(function()emu.setInput(input,0)end,emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
 if done then return end
 frame=frame+1;assert(frame<6500,'Physical Arthur pickup bound')
 if opening~='play'then
  if opening=='wait'and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then opening='play'else menu();return end
 end
 if not initial then
  if r('ArHostReady')~=167 then
   input={};if updates>=20 then return finish(false,'First actual Arthur initialization bound')end;return
  end
  initial=state();initial.score=score()
  assert(initial.lives==2 and initial.flags&32==0 and initial.weapon==64,'Normal armored Arthur first spawn')
  assert(r('CrossoverBehaviorVersion')==0 and r('WorldNumber')==0 and r('LevelNumber')==0,'Easy ordinary1-1')
  for _,n in ipairs(C.cheats)do assert(r(n)==0,'No active cheat '..n)end
 end
 observe()
 if updates~=lastUpdate then lastUpdate=updates;input=policy()end
end),emu.eventType.endFrame)
