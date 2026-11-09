-- Source-phase-aware continuation after the native first pipe proof.
local route={obstacles={
 {kind='pipe',left=608,right=640,top=160,lead=100},
 {kind='pipe',left=736,right=768,top=144,lead=100},
 {kind='pipe',left=912,right=944,top=144,lead=100},
 {kind='pit',left=1104,right=1136,lead=94},
 {kind='pit',left=1376,right=1424,lead=87},
 {kind='pit',left=2448,right=2480,lead=94}},
 index=1,mode='approach',pad={'right'},events={},clears={},max_x=0,last_engine=8,stationary=0}
local routeCSV
local function routeLog(tag,extra)
 require(#route.events<180,'Bounded full route event receipt')
 local s=state()
 s.tag=tag;s.Main=admitted;s.frame=frame;s.index=route.index;s.route_mode=route.mode;s.extra=extra
 route.events[#route.events+1]=s
end
local function routeWrite(ok,why)
 local output={passed=ok,reason=why,controller_only=true,emulated_writes=false,
  ROM_sha256=Q.ROM_sha256,first_pipe=pipeRoute.first_pipe_cleared,
  full_stage=ok,helpers_added=false,initial_lives=initialLives,
  final_lives=r('NumberofLives'),HP=ps(0x6cf),world=r('WorldNumber'),level=r('LevelNumber'),
  engine=r('GameEngineSubroutine'),state=state(),frames=frame,admitted=admitted,route=route}
 writejson('full11.json',output)
 if routeCSV then routeCSV:flush()end
end
local function routeFail(why)
 routeLog('terminal-obstruction')
 routeWrite(false,why)
 require(false,why)
end
local function routeMode(mode,pad)
 route.mode=mode;route.changed=admitted;route.pad=pad
 routeLog(mode)
end
local function routeBegin()
 route.start=admitted;route.last=admitted
 routeCSV=assert(io.open(OUTPUT..'full11-route.csv','w'))
 routeCSV:write('Main,frame,obstacle,route_mode,X,Y,foot,source_action,source_frame,source_mode,HP,lives,pad\n')
 routeLog('first-pipe-far-side-floor')
end
local function solid(x,y)
 if y<32 or y>=240 or x<0 then return false end
 local at=0x300+((x//256)&1)*208+(y&240)-32+((x&255)//16)
 local tile=ram(at)
 return ram(0xef36+tile)&1~=0,tile
end
local function runReady(s)
 return s.source_action==1 and s.source_mode==1 and s.source_frame>=6 and s.source_frame<=13
  and s.source_A_lock==0 and r('Player_State')==0
end
local function idleReady(s)
 return s.source_frame==15 and s.source_mode==0 and s.source_A_lock==0
  and r('Player_State')==0
end
local function actualSupport(s)
 if r('Player_State')~=0 or s.native_y_high~=1 then return false end
 local height=s.native_y+32
 return solid(s.world_x+2,height)or solid(s.world_x+13,height)
end
local function routeTarget(s)
 local best
 for i=0,5 do
  local flag=ram(L.Enemy_Flag+i);local id=ram(L.Enemy_ID+i);local status=ram(L.Enemy_State+i)
  local x=ram(L.Enemy_X_Position+i)+256*ram(L.Enemy_PageLoc+i)
  local y=ram(L.Enemy_Y_Position+i)
  local dx=x-s.world_x
  if flag>0 and flag<128 and id<=6 and status&32==0 and dx>=24 and dx<=100
     and math.abs(y-s.native_y)<=32 and (not best or dx<best.gap) then
   best={id=id,slot=i,x=x,y=y,gap=dx}
  end
 end
 return best
end
local function fullTick(finish)
 local engine=r('GameEngineSubroutine')
 if r('SelectedCharacter')~=38 or r('OperMode')~=1 then routeFail('Actual native owner lost')end
 if r('NumberofLives')~=initialLives or engine==11 or ps(0x6cf)==0 then routeFail('Actual original source or native death')end
 if r('WorldNumber')~=0 or r('LevelNumber')>1 then routeFail('Native stage advanced outside 1-1/1-2')end
 if r('LevelNumber')==1 and engine==8 and r('OperMode_Task')==3 and sourceActive() then
  if #route.clears~=6 or route.max_x<3100 or not route.flag then
   routeFail('Native 1-2 reached without all supported crossings and flagpole')
  end
  routeLog('actual-active-1-2')
  routeWrite(true,'All four pipes and three pits crossed with original source controls and native flag')
  shot('prince-active-1-2')
  routeCSV:close();csv:close();finish();return
 end
 if engine~=route.last_engine then
  routeLog('native-engine-transition',{before=route.last_engine,after=engine})
  route.last_engine=engine
 end
 if engine==4 and not route.flag then route.flag=true;routeLog('actual-native-flagpole');shot('prince-native-flagpole')end
 if engine~=8 then route.pad={'right'};return end
 if not sourceActive() then routeFail('Prince authentication absent during active stage')end
 headers()
 if admitted==route.last then return end
 route.last=admitted
 local s=state()
 local x=s.world_x
 route.max_x=math.max(route.max_x,x)
 if x==route.last_x then route.stationary=route.stationary+1 else route.stationary=0 end
 route.last_x=x
 if admitted-route.start>7600 or route.stationary>430 then
  routeFail('Bounded original movement could not advance')
 end
 if admitted%6==0 then
  routeCSV:write(table.concat({admitted,frame,route.index,route.mode,x,s.native_y,s.physical_foot,
    s.source_action,s.source_frame,s.source_mode,s.HP,s.lives,s.pad},',')..'\n')
  routeCSV:flush()
 end
 local o=route.obstacles[route.index]
 local support=actualSupport(s)
 local age=admitted-(route.changed or route.start)
 if o and x>=o.right+16 and support then
  if o.kind=='pipe' and not route.on_top then routeFail('Pipe far side lacks real native support on its top')end
  if o.kind=='pit' and not route.jump then routeFail('Pit crossing lacks actual original action4')end
  route.clears[#route.clears+1]={kind=o.kind,left=o.left,right=o.right,top=o.top,
      x=x,Main=admitted,observed_original_climb=route.hang,observed_support=route.on_top,
      original_jump=route.jump}
  routeLog('supported-far-side')
  route.index=route.index+1;route.hang=nil;route.on_top=nil;route.jump=nil;route.aerial_attempt=nil
  route.settled_attempt=nil;route.combat=nil
  routeMode('approach',{'right'});return
 end
 if o and o.kind=='pipe' and x+13>=o.left and x<o.right
    and support and math.abs((s.native_y+32)-o.top)<=2 and not route.on_top then
  route.on_top=s;routeLog('physical-native-pipe-top-supported')
  routeMode('pipe-cross',{'right'});return
 end
 if o and o.kind=='pipe' and (s.source_mode==2 or s.source_mode==6 or s.source_action==10)
    and (route.mode=='aerial' or route.mode=='stand-up' or route.mode=='pipe-climb') then
  if not route.hang then route.hang=s;routeLog('actual-original-ledge-hang')end
  if s.source_action==10 and s.physical_foot<=o.top+3 then
   routeMode('pipe-cross',{'right'})
  elseif route.mode~='pipe-climb' then routeMode('pipe-climb',{'up'})end
  return
 end
 if route.mode=='pipe-climb' then
  route.pad={'up','right'}
  if age>150 then routeFail('Original ledge climb did not gain authentic height')end
  return
 end
 if route.mode=='pipe-cross' then
  route.pad={'right'}
  if age>210 then routeFail('Native pipe-top crossing lost forward progress')end
  return
 end
 if route.mode=='takeoff' then
  route.pad={'right','a'}
  if s.source_action==4 then
   if route.combat then routeLog('actual-original-combat-jump',route.combat)else route.jump=s end
   routeMode('aerial',{'right'})
  elseif age>28 then
   if route.combat then routeFail('Fresh A did not admit original combat jump')end
   if not o or o.kind=='pit' then routeFail('Fresh A did not admit original pit jump')end
   routeMode('settle',{})
  end
  return
 end
 if route.mode=='aerial' then
  route.pad={'right'}
  if o and o.kind=='pipe' and not route.combat and x>=o.left-42 and x<o.right
     and s.physical_foot-24<=o.top+15 then route.pad={'right','up'} end
  if s.source_action~=4 and age>=12 and support then
   if route.combat then route.combat=nil;routeMode('approach',{'right'})
   elseif o and o.kind=='pipe' then routeMode('settle',{})
   else routeMode('approach',{'right'})end
  elseif age>128 then routeFail('Original airborne trajectory did not find native support')end
  return
 end
 if route.mode=='settle' then
  route.pad={}
  if idleReady(s) then
   route.settled_attempt=true;routeMode('stand-up',{'up'})
  elseif age>160 then routeFail('Original idle stance could not be obtained for Up')end
  return
 end
 if route.mode=='stand-up' then
  route.pad=age<64 and {'up'}or{'right','up','a','b'}
  if age>230 then routeFail('Standing and aerial ledge approaches did not reach this pipe')end
  return
 end
 route.pad={'right'}
 if runReady(s) and support then
  local enemy=routeTarget(s)
  if enemy and enemy.gap>=60 and enemy.gap<=86 and (not o or x<o.left-o.lead-8) then
   route.combat=enemy;routeMode('takeoff',{'right','a'});return
  end
  if o and x>=o.left-o.lead then
   if o.kind=='pit' and not route.jump then routeMode('takeoff',{'right','a'});return end
   if o.kind=='pipe' and not route.aerial_attempt and x<=o.left-67 then
    route.aerial_attempt=true;routeMode('takeoff',{'right','a'});return
   end
  end
 end
 if o and o.kind=='pipe' and x>=o.left-48 then routeMode('settle',{});return end
 if not o and support and x>=2700 and x<3070 then
  local foot=s.native_y+32
  if solid(x+20,foot-8) and not solid(x+20,foot-24) then
   route.pad={'right','up'}
  end
 end
end
