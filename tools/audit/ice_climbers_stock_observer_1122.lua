assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact published ROM')
local function r(name,i)
 return emu.read(assert(C.ram[name],name)+(i or 0),emu.memType.nesDebug)
end
local function pos(lo,hi,i) return r(lo,i)+256*r(hi,i) end
local function scope()
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
local function identity()
 return r('SelectedCharacter')==20 and r('IcVariant')==C.variant
  and r('CrossoverBehaviorVersion')==C.mode_value and r('CheatInvincible')==0 and r('CheatStartLevel')==0
end
local physical,polls,updates,motor,mask=0,0,0,0,0
local entered,done,nextMenuPoll=false,false,0
local expected=C.route=='life' and {0,3} or {0,1,2}
local item_x={[0]=336,1248,1616,1024}
local checks,heads,tail,pending,registered={},{},{},{},{}
local lifePending
for _,kind in ipairs(expected) do checks[tostring(kind)]={kind=kind} end

local function actor(i)
 return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),
  state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),
  y=r('Enemy_Y_Position',i),yHigh=r('Enemy_Y_HighPos',i)}
end
local function state()
 return {frame=physical,update=updates,motor=motor,x=pos('Player_X_Position','Player_PageLoc'),
  y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),
  vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),power=r('IcPower'),
  lives=r('NumberofLives'),star=r('StarInvincibleTimer'),engine=r('GameEngineSubroutine'),
  camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),world=r('WorldNumber'),level=r('LevelNumber')}
end
local function context()
 local c=state()
 c.poll=polls;c.char=20;c.variant=C.variant;c.r=r
 c.area=r('AreaPointer');c.areaType=r('AreaType');c.lastMask=mask;c.lastA=mask&128~=0
 c.grounded=c.state==0;c.stageFrame=physical-entered
 c.block=function(x,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',((x//256)&1)*208+((y//16)-2)*16+((x//16)&15))
 end
 c.enemy=function()
  local nearest
  for i=0,5 do
   local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and (a.id<0x15 or a.id==0x2d or a.id==0x33)
      and a.state<0x20 and not(a.id==6 and a.state>=2) and math.abs(dx)<160
      and (not nearest or math.abs(dx)<math.abs(nearest.dx)) then
    a.dx=dx;nearest=a
   end
  end
  return nearest
 end
 return c
end
local function json(v)
 local t=type(v)
 if t=='string' then return '"'..v:gsub('[%z\1-\31\\"]',function(c) return string.format('\\u%04x',c:byte()) end)..'"' end
 if t=='number' or t=='boolean' then return tostring(v) end
 if v==nil then return 'null' end
 local a={}
 if #v>0 then for i,x in ipairs(v) do a[i]=json(x) end;return '['..table.concat(a,',')..']' end
 for k,x in pairs(v) do a[#a+1]=json(tostring(k))..':'..json(x) end
 table.sort(a);return '{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,form=C.form,route=C.route,
  physical_frames=physical,input_polls=polls,updates=updates,movement_updates=motor,
  difficulty=r('CrossoverBehaviorVersion'),items=checks,head=heads,tail=tail,terminal=state(),
  phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0}))
 emu.stop(ok and 0 or 1)
end
local function guarded(label,callback)
 return function(...)
  if done then return end
  local ok,why=pcall(callback,...)
  if not ok then finish(false,label..': '..tostring(why)) end
 end
end
local function mapped(pc)
 local m=emu.convertAddress(pc)
 if not m then return -1 end
 if m.memType==emu.memType.nesPrgRom then return (m.address//8192)|128 end
 if m.memType==emu.memType.nesWorkRam then return m.address//8192 end
 return -1
end
local function authenticate(h)
 local mem=h.tag>=128 and emu.memType.nesPrgRom or emu.memType.nesWorkRam
 for i=1,#h.hex,2 do
  assert(emu.read(h.offset+(i-1)//2,mem)==tonumber(h.hex:sub(i,i+1),16),'Exact physical hook bytes')
 end
end
local function afterMain()
 if not entered then return end
 updates=updates+1
 local s=state()
 if #tail==6 then table.remove(tail,1) end
 tail[#tail+1]={x=s.x,y=s.y,update=updates,mask=mask,star=s.star}
 assert(identity() and s.world==0 and s.level==0 and s.engine~=11 and r('OperMode')~=3,'Living Ice Climber in ordinary 1-1')
 assert(updates<5100,'Bounded pickup route')
 for i=0,5 do
  local a=actor(i);local q=checks[tostring(a.kind)]
  if q and not q.birth and a.flag>0 and a.flag<128 and a.id==46 and a.state<128
     and math.abs(a.x-item_x[a.kind])<=2 then
   q.birth={actor=a,player=s}
  end
 end
 local complete=true
 for _,kind in ipairs(expected) do
  local q=checks[tostring(kind)]
  if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then
   if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')
   elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')
   else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end
   q.after=s
  end
  complete=complete and q.after~=nil
 end
 if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end
end

local function collected(p)
 local a=p.actor
 local q=checks[tostring(a.kind)]
 if not q or not q.birth or q.birth.actor.slot~=a.slot or q.collect then return end
 assert(r('Enemy_Flag',a.slot)==0 and r('FloateyNum_Control',a.slot)==(a.kind==3 and 11 or 6),
  'Normal pickup erase and reward popup')
 assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')
 local s=state()
 q.collect={actor=a,before=p.before,after=s,popup=r('FloateyNum_Control',a.slot),sound=r('Square2SoundQueue')}
 if a.kind<2 then
  assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')
 elseif a.kind==2 then
  assert(s.star==35 and r('AreaMusicQueue')==64 and s.power==p.before.power,'Native Star timer and music')
  q.collect.music=r('AreaMusicQueue')
 else
  assert(s.lives==p.before.lives,'1-UP awaits the native delayed credit')
  return
 end
 q.grant=s
end

local function settle()
 local cpu=emu.getState()
 local pc,sp=cpu['cpu.pc'],cpu['cpu.sp']
 if lifePending and pc==lifePending.pc and sp==lifePending.sp and mapped(pc)==lifePending.tag then
  local s=state()
  assert(s.lives==lifePending.lives+1,'Original 1-UP life counter increments')
  checks['3'].grant=s;lifePending=nil
 end
 while #pending>0 do
  local p=pending[#pending]
  if pc~=p.pc or sp~=p.sp or mapped(pc)~=p.tag then return end
  pending[#pending]=nil
  if p.name=='IcMovement' then motor=motor+1
  elseif p.name=='GameLoop' then afterMain()
  elseif p.actor then collected(p) end
 end
end
local function register(pc)
 if registered[pc] then return end
 registered[pc]=true
 emu.addMemoryCallback(guarded('Actual return',settle),emu.callbackType.exec,pc)
end
local function enter(name,h)
 if not entered or mapped(h.pc)~=h.tag then return end
 local cpu=emu.getState()
 local sp=cpu['cpu.sp']
 if name=='LifeCredit' then
  local q=checks['3']
  if q and q.collect and not q.grant and not lifePending then
   lifePending={pc=h.pc+3,sp=sp,tag=h.tag,lives=r('NumberofLives')};register(h.pc+3)
  end
  return
 end
 if name=='PlayerHeadCollision' then
  local s=state()
  for _,kind in ipairs(expected) do
   if not heads[tostring(kind)] and not checks[tostring(kind)].birth and math.abs(s.x+8-item_x[kind])<=22 then
    heads[tostring(kind)]={x=s.x,y=s.y,update=updates,tile=cpu['cpu.a']}
   end
  end
  return
 end
 local pc=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}
 if name=='HandlePowerUpCollision' then
  local a=actor(cpu['cpu.x']);local q=checks[tostring(a.kind)]
  if not(a.id==46 and a.flag>0 and q and q.birth and a.slot==q.birth.actor.slot and not q.collect) then return end
  p.actor=a;p.before=state()
 end
 pending[#pending+1]=p;register(pc)
end
for name,h in pairs(C.hooks) do
 emu.addMemoryCallback(guarded(name,function() enter(name,h) end),emu.callbackType.exec,h.pc)
end

local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function pulse(key)
 if polls<nextMenuPoll then return {} end
 nextMenuPoll=polls+8
 if type(key)=='number' then
  for k,v in pairs(bits) do if key==v then return {[k]=true} end end
  error('Unexpected menu button '..key)
 end
 return {[key]=true}
end
local function menu()
 if physical<45 or r('CrossoverTitleDrawn')==0 then return {} end
 local mode=r('CrossoverMenuState')
 if mode==0 then
  local focus=r('CrossoverBehaviorVersion')==C.mode_value and 0 or 1
  if r('CrossoverOptionsFocus')~=focus then return pulse('down') end
  return pulse(focus==0 and 'start' or 'a')
 elseif mode==4 then
  if r('CrossoverOptionsFocus')~=1 then return pulse('down') end
  if r('CrossoverBehaviorVersion')~=C.mode_value then return pulse('a') end
  return pulse('b')
 elseif mode==2 then
  local cursor=r('CrossoverMenuIndex')
  if cursor~=C.slot then return pulse(assert(C.navigation[cursor+1],'Compiled roster direction')) end
  if r('IcVariant')~=C.variant then return pulse('select') end
  assert(identity(),'Requested character, alternate and difficulty in menu')
  return pulse('start')
 end
 return {}
end
emu.addEventCallback(guarded('Controller',function()
 polls=polls+1
 local b=not entered and menu() or (scope() and choose(context()) or {})
 mask=0;for k,v in pairs(bits) do if b[k] then mask=mask|v end end
 emu.setInput(b,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded('Physical frame',function()
 physical=physical+1
 assert(physical<=6900,'Bounded physical replay')
 if not entered and scope() then
  assert(identity() and r('WorldNumber')==0 and r('LevelNumber')==0,'Natural first gameplay')
  for _,h in pairs(C.hooks) do authenticate(h) end
  entered=physical
 end
end),emu.eventType.endFrame)
