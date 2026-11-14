-- Normal controller inputs and readonly native witnesses. No game-state writes.
local frame,polls,updates,entries,age=0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local buttons,finished,lastA={},false,false
local first,flag,castle,entrance
local nextUpdates,maxX=0,0
local pendingReturn
local checkpoints,menuEvents={},{}
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function identity()return r('SelectedCharacter')==0 and r('MarioVariant')==C.variant and r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0 end
local function state()return {frame=frame,Main=updates,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),state=r('Player_State'),engine=r('GameEngineSubroutine'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaType'),power=r('PlayerStatus'),lives=r('NumberofLives'),variant=r('MarioVariant'),chr_mode=r('X5ChrMode'),star=r('StarInvincibleTimer')}end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local a={};if #v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(k)..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
end
local function finish(reason)
 if finished then return end;finished=true
 local ok=reason=='full-1-1-and25grounded-1-2'and first and flag and castle and entrance and nextUpdates==25 and identity()and r('NumberofLives')==2
 print('SMB_NATIVE_RECEIPT '..json({passed=not not ok,reason=reason,ROM_SHA256=C.sha,identity=C.key,name=C.name,Select_cycle=C.cycle,MarioVariant=C.variant,physical_frames=frame,input_polls=polls,Main_entries=entries,Main_returned=updates,Main_updates=updates,first_active=first,flag=flag,castle=castle,entrance=entrance,next_area_updates=nextUpdates,terminal=state(),max_x=maxX,checkpoints=checkpoints,menu_events=menuEvents,full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false,outputs=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if finished then return end;local ok,why=pcall(fn,...);if not ok then finish('callback-error:'..tostring(why))end end end
local function hook(name,fn)
 local h=C.hooks[name]
 emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesPrgRom or a.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact native hook '..name)end
  fn()
 end),emu.callbackType.exec,h.pc)
end
hook('GameLoop',function()
 assert(not pendingReturn,'Previous Main must return before another entry')
 local sp=emu.getState()['cpu.sp']
 local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 assert(ret==C.hooks.GameLoopReturn0.pc or ret==C.hooks.GameLoopReturn1.pc,'Exact compiled Main caller')
 entries=entries+1;pendingReturn={pc=ret,sp=(sp+2)&255}
end)
local function returned(pc)
 assert(pendingReturn and pendingReturn.pc==pc and pendingReturn.sp==emu.getState()['cpu.sp'],'Same Main caller/SP return')
 pendingReturn=nil;updates=updates+1
 if first and r('WorldNumber')==0 and r('LevelNumber')==1 and active()then
  if r('AreaType')==2 and r('Player_State')==0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<224 then
   nextUpdates=nextUpdates+1
   if nextUpdates==25 then finish('full-1-1-and25grounded-1-2')end
  else nextUpdates=0 end
 end
end
hook('GameLoopReturn0',function()returned(C.hooks.GameLoopReturn0.pc)end)
hook('GameLoopReturn1',function()returned(C.hooks.GameLoopReturn1.pc)end)
hook('FlagpoleRoutine',function()if first and not flag and identity()and r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 and pos('Player_X_Position','Player_PageLoc')>=3000 then flag=state()end end)
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,name)local began=frame;while not fn()and frame-began<limit do wait(1)end;assert(fn(),'Actual frontend '..name)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Explicit421 ROM pin')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Cold Easy/no cheats')
 press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 assert(r('CrossoverMenuIndex')==0 and r('SelectedCharacter')==0 and r('MarioVariant')==0,'Actual initial Mario')
 for i=1,C.cycle do press('select');menuEvents[i]={frame=frame,variant=r('MarioVariant'),raw=r('SelectedCharacter')}end
 assert(identity(),'Actual compiled alternate cycle')
 if C.key=='kamikaze'then assert(r('X5ChrMode')==0x84,'Actual Kamikaze skin publication')end
 press('start');menuDone=true
end)
local function context()
 local c={frame=frame,poll=polls,char=0,variant=C.variant,r=r,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=lastA,grounded=r('Player_State')==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16))end
 c.enemy=function()
  local nearest
  for i=0,5 do local id,st,f=r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_Flag',i)
   if f>0 and f<128 and(id<0x15 or id==0x2d or id==0x33)and st<32 and not(id==6 and st>=2)then
    local x=pos('Enemy_X_Position','Enemy_PageLoc',i);local dx=x-c.x
    if dx> -160 and dx<160 and(not nearest or math.abs(dx)<math.abs(nearest.dx))then nearest={slot=i,id=id,x=x,y=r('Enemy_Y_Position',i),state=st,dx=dx}end
   end
  end;return nearest
 end
 return c
end
local stairPhase,stairAge='approach',0
local function controls(c)
 if c.world~=0 or c.level~=0 or c.x<2360 or c.x>=2580 or stairPhase=='done'then return choose(c)end
 if stairPhase=='approach'then
  if c.x>=2396 and c.grounded then
   if c.lastA then return{}end
   stairPhase='rise';stairAge=0
  else return choose(c)end
 end
 if stairPhase=='rise'then
  if c.grounded and c.y<=112 and c.x>=2428 then stairPhase='release';return{}end
  stairAge=stairAge+1
  local velocity=c.vx<128 and c.vx or c.vx-256
  local stopping=c.x+velocity*math.abs(velocity)/32
  return {right=stopping<2432,left=stopping>2434,b=false,a=stairAge<=40}
 end
 if stairPhase=='release'then
  if c.lastA then return{}end
  stairPhase='cross';stairAge=0
 end
 if stairPhase=='cross'then
  if c.grounded and c.x>=2480 then stairPhase='done';return choose(c)end
  stairAge=stairAge+1;return {right=true,b=true,a=stairAge<=40}
 end
end
emu.addEventCallback(guard(function()
 polls=polls+1;local b=buttons
 if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end
 lastA=not not b.a;emu.setInput(b,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 if not first and active()and r('WorldNumber')==0 and r('LevelNumber')==0 then
  assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5,'Genuine initial1-1')
  first=state()
 end
 if first then
  if not identity()or r('NumberofLives')~=2 or r('GameEngineSubroutine')==11 or r('OperMode')==3 then finish('identity-life-or-death');return end
  local s=state();maxX=math.max(maxX,s.x)
  if s.level==0 and s.x>=256+#checkpoints*256 and #checkpoints<13 then checkpoints[#checkpoints+1]=s end
  if s.world==0 and s.level==0 and s.engine==5 and s.x>=3160 then castle=castle or s end
  if s.world==0 and s.level==1 and s.engine==0 then entrance=entrance or s end
  if s.world~=0 or s.level>1 or(s.level==1 and not(flag and castle))then finish('shortcut-or-unexpected-stage');return end
 end
 if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end
end),emu.eventType.endFrame)
