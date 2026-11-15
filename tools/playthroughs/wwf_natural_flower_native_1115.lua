-- Ordinary controller only. Actual native collectors, freeze and movement calls.
local frame,completed,entries,moves,polls,pad=0,0,0,0,0,0
local stopped,menuDone=false,CPU_CONTROLLER_OPENING or false
local pendingMain,pendingPickup,firstJump,travelJump,crossStart
local phase,pipe,cooldown,retreatSettle='first-M',0,0,0
local items,events,returnHooks={},{},{}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local out={};if#v>0 then for i,x in ipairs(v)do out[i]=json(x)end;return'['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10,'Decimal score');n=n*10+d end;return n end
local function state()return{Main=completed,frame=frame,moves=moves,phase=phase,x=r('Player_X_Position')+256*r('Player_PageLoc'),
 y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vy=r('Player_Y_Speed'),vx=r('Player_X_Speed'),
 facing=r('PlayerFacingDir'),engine=r('GameEngineSubroutine'),power=r('PlayerStatus'),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),
 lives=r('NumberofLives'),score=score()}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i),kind=r('PowerUpType',i),
 x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function identity()
 assert(r('SelectedCharacter')==29 and r('FmGroups')&7==C.role,'Actual WWF identity')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Ordinary uncheated input')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2,'Living authored1-1')
end
local function finish(ok,why)
 if stopped then return end;stopped=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,identity=C.key,ROM_SHA256=C.sha,Main_entries=entries,Main_returns=completed,
 physical_frames=frame,input_polls=polls,WfMovement_calls=moves,items=items,events=events,terminal=state(),
 gameplay_seeds=0,normal_controller_only=true,output_files=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function change(name)phase=name;assert(#events<32,'Bounded phase trace');events[#events+1]=state()end
local function hook(h,fn)
 emu.addMemoryCallback(guard(function()
  local q=emu.convertAddress(h.pc);if not q or q.memType~=emu.memType.nesPrgRom or q.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact current native hook')end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function near(s)
 for i=0,5 do local a=actor(i);if a.flag>0 and a.flag<128 and a.id<21 and a.state&32==0 and a.x>s.x and a.x-s.x<=44 and math.abs(a.y-s.y)<40 then return true end end
 return false
end
local function punch()return completed%18<3 and(C.role==3 and 68 or 64)or 0 end
local function solid(x,y)
 if y<32 or y>=240 then return false end
 local index=(x//256)%2*208+((y-32)//16)*16+(x%256)//16
 local t=r('Block_Buffer_1',index);return t~=0 and t~=35 and t~=38 and t~=194 and t~=195
end
local function drive()
 if not menuDone then return end;identity();local s=state();assert(completed<4600,'M/F completedMain bound')
 for i=0,5 do local a=actor(i)
  if a.flag==1 and a.id==46 and(a.x<600 or a.x==1248)then
   local kind=a.x<600 and 0 or 1;assert(a.kind==kind,'Authored item kind')
   if not items[kind]then items[kind]={born={state=s,actor=a},ticks=0}end
   if a.state>=128 and not items[kind].mature then items[kind].mature={state=s,actor=a}end
  end
 end
 pad=0
 if s.active~=0 then assert(phase=='freeze-M'or phase=='freeze-F','Collector owns freeze');return end
 if phase=='freeze-M'or phase=='freeze-F'then
  local k=phase=='freeze-M'and 0 or 1;local it=items[k]
  assert(it.ticks==60 and s.power==k+1 and active(),'Actual60-tick powerup recovery');it.recovered=s;it.resume_moves=moves;change(k==0 and'post-M'or'post-F');return
 end
 if phase=='post-M'or phase=='post-F'then
  local k=phase=='post-M'and 0 or 1;local it=items[k];it.resumed=moves-it.resume_moves
  if it.resumed>=25 then
   assert(it.resumed==25 and s.score>=it.collected.before.score+1000,'Score and25 actual resumed movements');it.ready=s
   if k==1 then finish(true,'Real M and Flower with60-tick transactions and25 resumed moves each')else change('travel')end
  end;return
 end
 if not active()then return end
 if phase=='first-M'then
  if firstJump and completed-firstJump<18 then pad=128
  elseif near(s)then pad=punch()
  elseif not firstJump and s.x>=328 then firstJump=completed;pad=128
  else pad=s.x<401 and 1 or 0 end
 elseif phase=='travel'then
  local starts,ends={404,564,692,868},{484,644,772,948}
  if pipe<4 and s.x>=ends[pipe+1]and s.native==0 then pipe=pipe+1 end
  if s.x>=1184 and s.native==0 then assert(s.power==1,'Earned Mushroom armor');change('flower-align')
  else
   pad=1
   if travelJump then
    local age=completed-travelJump;if age<4 or s.vy>=128 then pad=129 end
    if age>12 and s.native==0 then travelJump=nil;cooldown=8 end
   elseif cooldown>0 then cooldown=cooldown-1
   elseif s.native==0 then
    if(pipe<4 and s.x>=starts[pipe+1])or(pipe>=4 and(not solid(s.x+8,216)or solid(s.x+28,s.y+24)))then travelJump=completed;pad=129
    elseif near(s)then pad=punch()end
   end
  end
 elseif phase=='flower-align'then
  if near(s)then pad=punch()elseif s.x<1242 then pad=1 elseif s.x>1245 then pad=2
  elseif s.native==0 then assert(s.power==1,'Powered authored head approach');firstJump=completed;pad=128;change('flower-spawn')end
 elseif phase=='flower-spawn'then
  if items[1]then change('flower-mature')else assert(completed-firstJump<120,'Flower head admission');if completed-firstJump<24 then pad=128 end end
 elseif phase=='flower-mature'then
  if items[1].mature and s.native==0 then change('flower-retreat')end
 elseif phase=='flower-retreat'then
  if s.x>1200 then pad=2 elseif s.native==0 then retreatSettle=retreatSettle+1;if retreatSettle>=4 then pad=1;change('flower-runup')end end
 elseif phase=='flower-runup'then
  assert(s.x<1220,'Right-facing run-up bound');pad=1
  if s.native==0 and s.facing==1 and s.x>=1206 then crossStart=completed;pad=129;change('flower-cross')end
 elseif phase=='flower-cross'then
  assert(completed-crossStart<160,'Flower roof approach bound');pad=s.x<1245 and 1 or(s.x>1253 and 2 or 0)
  if completed-crossStart<4 or s.vy>=128 then pad=pad|128 end
 end
end
hook(C.hooks.WfMovement,function()if menuDone then moves=moves+1 end end)
hook(C.hooks.GuestPowerupUpdate,function()
 if not menuDone or r('GuestPowerupActive')==0 then return end
 local k=phase=='freeze-M'and 0 or 1;local it=assert(items[k]);assert(it.collected and r('GuestPowerupAge')==it.ticks,'Actual freeze age');it.ticks=it.ticks+1;assert(it.ticks<=60,'Freeze maximum60')
end)
hook(C.hooks.HandlePowerUpCollision,function()
 if not menuDone then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 if a.flag~=1 or a.id~=46 then return end
 local k=a.kind;local it=assert(items[k],'Observed authored birth');assert(k==0 or k==1,'M/F only')
 assert(it.mature and a.state>=128 and not it.collected and not pendingPickup,'Mature physical collector')
 local sp=cpu['cpu.sp'];local ret=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1;local mapping=assert(emu.convertAddress(ret))
 pendingPickup={slot=i,kind=k,sp=(sp+2)&255,pc=ret,map=mapping,before=state(),actor=a}
 if not returnHooks[ret]then
  returnHooks[ret]=true;emu.addMemoryCallback(guard(function()
   local p=pendingPickup;if not p or p.pc~=ret or emu.getState()['cpu.sp']~=p.sp then return end
   local actual=assert(emu.convertAddress(ret));assert(actual.memType==p.map.memType and actual.address==p.map.address,'Actual collector return map')
   local f=actor(p.slot);assert(emu.getState()['cpu.ps']&1~=0 and f.flag==0 and r('FloateyNum_Control',p.slot)==6,'Actual collector carry/erase/popup6')
   assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('GameEngineSubroutine')==9 and r('TimerControl')==255,'Native transaction admission')
   assert(r('Square2SoundQueue')&32~=0,'Powerup cue producer')
   items[p.kind].collected={before=p.before,after=state(),actor=p.actor,PC=ret,SP=p.sp,cue=r('Square2SoundQueue')}
   pendingPickup=nil;change(p.kind==0 and'freeze-M'or'freeze-F')
  end),emu.callbackType.exec,ret)
 end
end)
hook(C.hooks.GameLoop,function()
 assert(not pendingMain,'Prior Main returned');local sp=emu.getState()['cpu.sp']
 local ret=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(ret==C.hooks.GameLoopReturn0.pc or ret==C.hooks.GameLoopReturn1.pc,'Actual Main caller');pendingMain={pc=ret,sp=(sp+2)&255};entries=entries+1
end)
for i=0,1 do local h=C.hooks['GameLoopReturn'..i];hook(h,function()
 assert(pendingMain and pendingMain.pc==h.pc and pendingMain.sp==emu.getState()['cpu.sp'],'Actual Main return PC/SP');pendingMain=nil;completed=completed+1;drive()
end)end
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)pad=bits;frames(4);pad=0;frames(10)end
local function ready(fn)for _=1,1000 do if fn()then return end;coroutine.yield()end;error('Cold readiness bound')end
local task=coroutine.create(function()
 if not CPU_CONTROLLER_OPENING then
  ready(function()return frame>=90 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end);press(16)
  ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
  assert(r('CrossoverMenuIndex')==0,'Initial Mario slot');for _,bits in ipairs(C.navigation)do press(bits)end
  assert(r('CrossoverMenuIndex')==C.slot and r('SelectedCharacter')==29 and r('FmGroups')&7==C.role,'Compiled wrestler slot/role');press(16);ready(active)
 end
 menuDone=true;identity();while not stopped do coroutine.yield()end
end)
emu.addEventCallback(guard(function()
 polls=polls+1;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;assert(frame<12000,'Physical bound12000');local ok,why=coroutine.resume(task);assert(ok,why)
end),emu.eventType.endFrame)
