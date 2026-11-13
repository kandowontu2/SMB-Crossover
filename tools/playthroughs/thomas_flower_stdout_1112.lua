-- Controller-only 1-1 mushroom, four lifts, and the authored flower.
local sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local mode=tonumber(os.getenv('SMB_TEST_VARIANT')or '0')
local frame,main,pad,epoch,opening=0,0,0,0,0
local game,done,mainReturn,pending=false,false,nil,nil
local phase,phaseEpoch,lift,previousY='opening',0,1,nil
local pickups,ticks,births,matures,crossings,history={},{0,0},{},{},{},{}
local flowerAttempts,flowerPeak,lastJump,flowerHelper,helperY,helperBirth=0,255,false,nil,nil,nil
local lifts={{400,176},{560,160},{688,144},{864,144}}
local function r(at)return emu.read(at,emu.memType.nesDebug)end
local function word(lo,hi)return r(lo)+256*r(hi)end
local function state()
 return {x=word(0x75,0x5c),y=r(0xbd),state=r(0x1e),status=r(0x75b),engine=r(0x0f),
         lives=r(0x75f),active=r(0x6bfd),age=r(0x6bfe),timer=r(0x74a),frame=frame,main=main,epoch=epoch,phase=phase}
end
local function actor(i)
 return {slot=i,flag=r(0x10+i),id=r(0x17+i),state=r(0x1f+i),kind=r(0x34+i),
         x=word(0x76+i,0x5d+i),y=r(0xbe+i),contact=r(0x566+i)}
end
local function json(v)
 local t=type(v)
 if t=='string'then return '"'..v:gsub('[%z\1-\31\\"]',function(c)
  if c=='"'then return '\\"'elseif c=='\\'then return '\\\\'end
  return string.format('\\u%04x',string.byte(c))
 end)..'"'end
 if t=='number'or t=='boolean'then return tostring(v)end
 assert(t=='table');local a={}
 if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end
 table.sort(a);return '{'..table.concat(a,',')..'}'
end
local function finish(ok,reason)
 if done then return end
 done=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=sha,controller_only=true,
  physical_frames=frame,Main=main,route_updates=epoch,pickups=pickups,births=births,matures=matures,
  progression=ticks,crossings=crossings,flower_jumps=flowerAttempts,flower_minimum_y=flowerPeak,
  flower_helper=flowerHelper or false,flower_helper_birth=helperBirth or false,recent=history,terminal=state()}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name,fn)
 return function(...)
  if done then return end
  local ok,why=pcall(fn,...)
  if not ok then finish(false,name..': '..tostring(why))end
 end
end
local function mapped(pc,bank)
 local q=emu.convertAddress(pc)
 return q and q.memType==emu.memType.nesPrgRom and q.address==bank*8192+(pc&8191)
end
local function ret(cpu)
 local sp=cpu['cpu.sp']
 return word(256+((sp+1)&255),256+((sp+2)&255))+1,(sp+2)&255
end
local function phaseTo(nextPhase)phase,phaseEpoch=nextPhase,epoch end
local function solid(x,y)
 if y<32 or y>=240 then return false end
 local t=r(0x300+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
end
local function hostile(s,actors)
 for _,a in ipairs(actors)do
  local dx=a.x-s.x
  if a.flag<128 and a.id<21 and a.state&32==0 and dx>0 and dx<=38 and math.abs(a.y-s.y)<=24 then return true end
 end
 return false
end
local function control(s,actors)
 local x,y,ground=s.x,s.y,s.state==0
 local age=epoch-phaseEpoch
 if s.active~=0 then return 0 end
 if #pickups>=2 then return 2 end
 if phase=='approach'then
  if x>=325 then phaseTo('first-jump');return 73 end
  return 65
 elseif phase=='first-jump'then
  if age>=8 then phaseTo('park');return 65 end
  return 73
 elseif phase=='park'then
  if #pickups==0 then return x<400 and 65 or 0 end
  phaseTo('retry');age=0
 elseif phase=='flower-approach'then
  if x>=1238 and ground then phaseTo('flower-wait');return 8 end
  if hostile(s,actors)then return 4+(epoch%24<6 and 64 or 0)end
  if ground and x>=1000 and epoch%8<3 and (solid(x+20,y+31) or not solid(x+12,y+32))then return 9 end
  return 1
 elseif phase=='flower-wait'then
  if #pickups>=2 then return 1 end
  local flower=nil
  for _,a in ipairs(actors)do if a.id==46 and a.kind==1 then flower=a;break end end
  if flower and mode==1 then phaseTo('flower-lift-retreat');return 2 end
  if flower and flower.state&128~=0 then
   flowerPeak=math.min(flowerPeak,y)
   if not ground and not lastJump then flowerAttempts=flowerAttempts+1;lastJump=true end
   if ground then lastJump=false end
   if mode==2 and ground and flowerAttempts>=5 then
    assert(#pickups==1 and ticks[1]==60 and #crossings==4 and s.status==1 and flower.y==119,
           'Reach probe preserved first upgrade and mature native flower')
    finish(true,'Mature flower remained uncollected after five ordinary jumps');return 0
   end
  end
  if flower and flower.state&128~=0 and ground then return (x<flower.x-8 and 1 or x>flower.x-2 and 2 or 0)+8 end
  if not flower and ground and age>30 and age%24<4 then return 8 end
  return 0
 end
 if phase:find('flower%-lift%-')then
  local helper=nil
  for _,a in ipairs(actors)do if a.flag==1 and a.id==37 and a.x==1200 then helper=a;break end end
  local previous=helperY;helperY=helper and helper.y or nil
  local boarded=helper and helper.contact==helper.slot
  if phase=='flower-lift-retreat'then
   if x>1176 or not ground then return 2 end
   phaseTo('flower-lift-wait');return 0
  elseif phase=='flower-lift-wait'then
   if helper and helper.y>=188 and (not previous or helper.y>=previous)then phaseTo('flower-lift-runup')end
   return 0
  elseif phase=='flower-lift-runup'then
   if age>=6 then phaseTo('flower-lift-hop')end
   return 1
  elseif phase=='flower-lift-hop'then
   if x>=1214 or age>=64 then
    if boarded then phaseTo('flower-lift-ride');flowerHelper={boarded=s,actor=helper}
    elseif ground or age>=64 then phaseTo('flower-lift-retreat')end
    return 0
   end
   return age<3 and 9 or 1
  elseif phase=='flower-lift-ride'then
   if boarded and y<=96 then phaseTo('flower-lift-depart');flowerHelper.depart=s
   elseif ground and not boarded then phaseTo('flower-lift-retreat')end
   return 0
  end
  assert(phase=='flower-lift-depart',phase)
  if #pickups<2 and ground and x>1270 then phaseTo('flower-lift-retreat');return 2 end
  return 1
 end
 local left,top=lifts[lift][1],lifts[lift][2]
 local ly,boarded=nil,false
 for _,a in ipairs(actors)do
  if a.flag==1 and a.id==37 and a.x==left then ly=a.y;boarded=a.contact==a.slot;break end
 end
 local oldY=previousY;previousY=ly
 if x>=left+96 then
  crossings[#crossings+1]={x=x,pipe=left+48,epoch=epoch,status=s.status}
  lift=lift+1;previousY=nil
  phaseTo(lift>#lifts and 'flower-approach' or 'approach-lift')
  return 1
 end
 if hostile(s,actors)then
  if not boarded and (phase=='runup'or phase=='hop')then phaseTo('retry')end
  return 4+(epoch%24<6 and 64 or 0)
 end
 if phase=='retry'then
  if boarded and x>=left+14 then phaseTo('ride')
  elseif ground and x>left-24 then return 2
  elseif ground then phaseTo('wait')end
  return 0
 elseif phase=='approach-lift'then
  if x>=left-24 then phaseTo('wait');return 0 end
  return 1
 elseif phase=='wait'then
  if ly and ly>=188 and (not oldY or ly>=oldY)then phaseTo('runup')end
  return 0
 elseif phase=='runup'then
  if age>=6 then phaseTo('hop')end
  return 1
 elseif phase=='hop'then
  if x>=left+14 or age>=64 then
   if boarded then phaseTo('ride')elseif ground or age>=64 then phaseTo('retry')end
   return 0
  end
  return age<3 and 9 or 1
 elseif phase=='ride'then
  if boarded and y+32<=top-16 then phaseTo('cross')
  elseif ground and not boarded then phaseTo('retry')end
  return 0
 end
 assert(phase=='cross',phase)
 return age>=6 and age<9 and 9 or 1
end
local function drive()
 if not game then return end
 local s=state()
 assert(r(0x6002)==10 and r(0x5fe5)&68==64,'Thomas owner')
 assert(r(0x764)==0 and r(0x761)==0 and r(0x7ffb)==0 and r(0x7ffc)==0,'1-1 and cheats off')
 assert(s.lives==2 and s.engine~=11,'Route life and death check')
 assert(epoch<4400,'Logical route bound')
 if opening<60 then
  pad=opening<4 and 0 or opening<36 and 1 or opening<52 and 129 or 1
  opening=opening+1;return
 elseif phase=='opening'then phaseTo('approach')end
 local actors={}
 for i=0,5 do
  local a=actor(i)
  if a.flag~=0 then
   actors[#actors+1]=a
   if a.id==46 and a.kind<=1 then
    births[a.kind+1]=births[a.kind+1]or a
    if a.state&128~=0 then matures[a.kind+1]=matures[a.kind+1]or a end
   end
  end
 end
 if epoch%24==0 then
  if #history==12 then table.remove(history,1)end
  history[#history+1]=s
 end
 if #pickups==2 and s.active==0 and s.status==2 and math.abs(s.x-pickups[2].player.x)>=16 then
  assert(ticks[1]==60 and ticks[2]==60 and #crossings==4 and s.timer==0 and s.engine==8,'Exact recovery')
  assert(mode~=2,'Reach diagnostic expected no flower pickup')
  assert(mode~=1 or helperBirth and flowerHelper and flowerHelper.depart,'Observed native lift construction, board and departure')
  finish(true,'Earned mushroom and flower, then resumed movement');return
 end
 pad=control(s,actors);epoch=epoch+1
end
local function pause(n)for _=1,n do coroutine.yield()end end
local function press(b)pad=b;pause(4);pad=0;pause(8)end
local function ready(fn)
 for _=1,900 do if fn()then return end;coroutine.yield()end
 error('Menu readiness bound')
end
local boot=coroutine.create(function()
 ready(function()return frame>=70 and r(0x6004)==1 and r(0x775)==0 end)
 press(16);ready(function()return r(0x7307)==2 and r(0x775)==0 end)
 assert(r(0x7309)==0,'Initial menu slot')
 for _,b in ipairs({4,1,1,32,32})do press(b)end
 assert(r(0x7309)==10 and r(0x6002)==10 and r(0x5fe5)&68==64,'Thomas selection')
 press(16);ready(function()return r(0x771)==1 and r(0x773)==3 and r(0x0f)==8 end)
 game=true;drive();while not done do coroutine.yield()end
end)
local function exec(pc,name,fn)
 emu.addMemoryCallback(guarded(name,fn),emu.callbackType.exec,pc)
end
exec(0xb341,'Thomas native lift constructor',function()
 if not game then return end
 local location=emu.convertAddress(0xb341)
 if not location or location.memType~=emu.memType.nesWorkRam or location.address~=3*8192+0x1341 then return end
 local slot=emu.getState()['cpu.x']
 if slot>=6 then return end
 local a=actor(slot)
 if a.x~=1200 then return end
 local left=word(0x71f,0x71d);local right=word(0x720,0x71e)
 assert(not helperBirth and a.id==37 and a.flag==1 and a.y==192,'Flower lift native placement')
 assert(r(0xb341)==0x20 and r(0xb342)==0x5a and r(0xb343)==0x01,'Existing native constructor call')
 assert(a.x-left>=256 and a.x-left<=287 and a.x>right,'Flower lift starts beyond camera right')
 helperBirth={actor=a,frame=frame,epoch=epoch,camera_left=left,camera_right=right,relative_left=a.x-left,center=a.x+16}
end)
exec(0x82d9,'GameLoop',function()
 if not mapped(0x82d9,126)then return end
 assert(not mainReturn,'Synchronous Main')
 local pc,sp=ret(emu.getState())
 assert(pc==0x82be or pc==0x82d0,'Native IdleLoop return')
 mainReturn={pc,sp}
end)
for _,pc in ipairs({0x82be,0x82d0})do
 exec(pc,'GameLoop return',function()
  local cpu=emu.getState()
  if mainReturn and mapped(pc,126)and mainReturn[1]==pc and mainReturn[2]==cpu['cpu.sp']then
   mainReturn=nil;main=main+1;drive()
  end
 end)
end
local registered={}
exec(0x9b28,'Native collector',function()
 if not game or not mapped(0x9b28,126)then return end
 local cpu=emu.getState();local a=actor(cpu['cpu.x']);local which=#pickups+1
 assert(not pending and which<=2 and a.flag==1 and a.id==46 and a.kind==which-1 and a.state&128~=0,'Mature native actor')
 local pc,sp=ret(cpu);pending={pc=pc,sp=sp,item=a,player=state(),sound=0}
 if not registered[pc]then
  registered[pc]=true
  exec(pc,'Collector return',function()
   local c=emu.getState();local q=pending
   if not q or q.pc~=pc or q.sp~=c['cpu.sp']then return end
   pending=nil;local i=q.item.slot;local now=state()
   assert((c['cpu.ps']or c['cpu.p'])&1~=0 and r(0x10+i)==0 and r(0x10d+i)==6 and q.sound>0,'Native pickup effects')
   assert(births[q.item.kind+1],'Authored actor observed before collection')
   matures[q.item.kind+1]=matures[q.item.kind+1]or q.item
   assert(now.active==1 and now.age==0 and now.engine==9 and now.timer==255,'Hosted freeze starts')
   pickups[#pickups+1]=q
  end)
 end
end)
exec(0xb299,'Native progression',function()
 if game and mapped(0xb299,10)and r(0x6bfd)~=0 then
  local which=#pickups
  assert(which>=1 and which<=2 and r(0x6bfe)==ticks[which]and ticks[which]<60,'Native progression age')
  ticks[which]=ticks[which]+1
 end
end)
emu.addMemoryCallback(guarded('Pickup sound',function(_,value)
 if pending and value==32 then pending.sound=pending.sound+1 end
end),emu.callbackType.write,0x104)
emu.addEventCallback(guarded('Controller poll',function()
 emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,
               select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded('Physical frame',function()
 frame=frame+1;assert(frame<12500,'Physical frame bound')
 local ok,why=coroutine.resume(boot);assert(ok,why)
end),emu.eventType.endFrame)
