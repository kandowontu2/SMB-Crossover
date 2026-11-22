-- Full-route fragments joined to the frozen native smoke lifecycle by Root's
-- strict builder. Terrain/enemy sensor code is injected byte-exactly from the
-- previously proven ordinary 1-1 controller. This file contains no state writes.
local routeEvents,jumpRequests,supportSamples={},{},{}
local routeClock,lastJump,bestX,advancedAt,grounded12,lastRouteMotor=0,-100,40,0,0,0
local eventOrder,lastPhase=0,nil

-- FULL_ROUTE_FINISH
local function finish(ok,why)
 if done then return end;done=true;pad=0
 local good,s=pcall(state);if not good then s={snapshot_error=tostring(s)}end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,form=C.form,character=C.name,
  run_kind='full11',physical_frames=frame,input_polls=polls,Main=mains,accepted_motor=motor,
  active_route_updates=routeClock,cold=cold,events=routeEvents,jumps=jumpRequests,
  grounded_1_2_returns=grounded12,support_samples=supportSamples,tail=tail,terminal=s,counts=counts,pending=#pending,
  controller_only=true,no_game_actor_inventory_health_seeds=true,no_shortcut_down_input=true,
  real_native_support_required=true,files=0,images=0,
  scope='Actual selected owner/constructor and returned native 1-1 flag/castle/1-2 entrance, then25 living grounded accepted source/Main returns supported by actual native block-buffer cells. No all-pickup, interrupt, artwork, audio, cadence or full Sonic3 fidelity claim.'}))
 emu.stop(ok and 0 or 1)
end

-- FULL_ROUTE_FUNCTIONS
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
FULL_ROUTE_SENSORS
local function nativeSupport(s)
 local x,y=s.x+12,s.y+32
 assert(y>=32 and y<240 and solid(x,y),'Actual buffered native floor supports grounded endpoint')
 local column=x>>4
 local at=0x300+((x>>8)&1)*208+((y>>4)-2)*16+(column&15)
 local tile=read(at)
 return{world_x=x,screen_y=y,buffer_address=at,tile=tile,attributes=r('MTileAttribute',tile),
  native_x=s.x,native_y=s.y,source_foot=s.foot,source_flags=s.flags,motor=motor,Main=mains}
end
local function recordEvent(name,s)
 if routeEvents[name]then return end
 local expected=({flag=1,castle=2,entrance=3})[name]
 assert(eventOrder+1==expected,'Native flag/castle/entrance order '..name)
 eventOrder=expected;routeEvents[name]=s
end
local function drive(s)
 local bits=routeClock>3 and 1 or 0
 if s.state==0 and s.flags&128~=0 and routeClock-lastJump>24 then
  local why=jumpReason(s)
  if why then
   assert(#jumpRequests<64,'Proven route jump bound64')
   lastJump=routeClock;jumpRequests[#jumpRequests+1]={reason=why,requested=s,motor=motor,clock=routeClock}
  end
 end
 if routeClock-lastJump<20 then bits=bits|128 end
 routeClock=routeClock+1;assert(routeClock<=3500,'Proven ordinary route update bound3500')
 if s.x>bestX then bestX=s.x;advancedAt=routeClock end
 assert(routeClock-advancedAt<120,'Ordinary controller route stalled')
 assert(bits&4==0,'No shortcut Down input')
 pad=bits
end
local function afterMain()
 if not game then return end
 assert(identity()and r('WorldNumber')==0 and r('LevelNumber')<=1,'Actual selected owner/world/level')
 assert(r('NumberofLives')==2 and r('GameEngineSubroutine')~=11,'Living native route without lost life')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats');headers()
 local s=state();local progressed=motor>lastRouteMotor;lastRouteMotor=motor
 local label=tostring(s.level)..':'..tostring(s.engine)
 if label~=lastPhase then bounded(phases,{phase=label,state=s},12);lastPhase=label end
 bounded(tail,{state=s,requested=pad,motor_progressed=progressed},8)
 if s.level==0 and s.engine==4 and s.x>=3000 then
  assert((counts.FlagpoleCollision_entries or 0)>0,'Actual native flagpole entry before flag state')
  recordEvent('flag',s)
 elseif s.level==0 and s.engine==5 and s.x>=3000 then recordEvent('castle',s)
 elseif s.level==1 and s.engine==7 then recordEvent('entrance',s)end
 if s.mode~=1 or s.task~=3 or s.engine~=8 then pad=0;return end
 assert(s.ready==1,'Ordinary movement owner ready')
 assert((s.width==24 or (s.hurt&64~=0 and s.width==28))
        and(s.height==24 or s.height==32),'Owned body or actual hurt pose')
 if progressed then
  assert(s.frame_status==0,'Accepted movement transaction available')
  assert(s.x==s.sx//256 and s.y==(s.foot//256-32)&255,'Actual native projection of source feet')
 end
 if s.level==1 then
  assert(eventOrder==3 and routeEvents.flag and routeEvents.castle and routeEvents.entrance,'Full native progression before1-2')
  assert(s.area==0 and s.area_type==2,'Actual underground1-2')
  pad=0
  local grounded=s.yhigh==1 and s.y==176 and s.state==0 and s.flags&128~=0 and s.vy==0
  if not grounded then grounded12=0
  elseif progressed then
   local support=nativeSupport(s)
   grounded12=grounded12+1
   if grounded12==1 or grounded12==25 then supportSamples[#supportSamples+1]=support end
  end
  if grounded12>=25 then
   for name in pairs(H)do
    if not C.fatal[name]then assert(counts[name..'_entries']==counts[name..'_returns'],'Balanced full-route '..name)end
   end
   assert(#pending==0 and(counts.MetaFeet_returns or 0)>=25,'Actual returned native foot services')
   finish(true,'Full native1-1 flag/castle/entrance plus25 living grounded1-2 returns')
  end
  return
 end
 assert(s.level==0 and s.area==5,'Actual authored1-1 area')
 assert(s.frame_status==0,'Ordinary1-1 transaction available')
 if progressed then drive(s)end
end
