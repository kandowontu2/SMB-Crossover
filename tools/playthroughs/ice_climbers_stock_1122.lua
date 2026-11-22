-- Inject ICE_STOCK_BASE with the unchanged ice_climbers_11_v2.lua drive.
-- This file returns drive(c), using that same context. ICE_STOCK_MODE is
-- 'flower-star' (default) or 'life'. c.update is the completed Main clock;
-- c.frame stays physical for the frozen prefix. No game-state writes.
-- Additional RAM reads: IcPower, StarInvincibleTimer, NumberofLives.
-- ICE_STOCK_STATE is policy telemetry, not an authoritative pickup receipt.
local base=assert(ICE_STOCK_BASE,'Inject the frozen Ice drive')
local mode=ICE_STOCK_MODE or 'flower-star'
assert(mode=='flower-star' or mode=='life','Unknown Ice stock route')
local S={version=1,mode=mode,phase='first-mushroom',attempts=0,changes={}}
ICE_STOCK_STATE=S
local target,clock,lastClock,cached=nil,0,nil,nil
local previousX,still=nil,0
local phaseAt,pulseUntil,creditAt,routeAt=0,-1,nil,nil
local seen,geometry,minimumY=false,nil,255
local baselineLives=nil

local function snapshot(c)
 return {update=clock,frame=c.frame,x=c.x,y=c.y,power=c.r('IcPower'),
  lives=c.r('NumberofLives'),star=c.r('StarInvincibleTimer')}
end
local function phase(name,c)
 S.phase=name;phaseAt=clock
 local q=snapshot(c);q.phase=name;q.target=target and target.kind or nil
 S.changes[#S.changes+1]=q
 if #S.changes>24 then table.remove(S.changes,1)end
end
local function fail(reason,c)
 S.failure=reason;S.terminal=snapshot(c)
 error('Ice stock policy: '..reason)
end
local function solid(c,x,y)
 local t=c.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function floor(c)return c.grounded and c.y>=168 end
local function direction(n)return n>0 and {right=true} or n<0 and {left=true} or {}end
local function moveToward(c,x,tolerance)
 local dx=x-c.x
 return direction(dx>(tolerance or 0) and 1 or dx< -(tolerance or 0) and -1 or 0)
end
local function item(c,kind)
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i)
  if flag>0 and flag<128 and c.r('Enemy_ID',i)==0x2e and c.r('PowerUpType',i)==kind then
   return {slot=i,kind=kind,state=c.r('Enemy_State',i),
    x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
  end
 end
end
local function chooseTarget(kind,c)
 target={kind=kind,id=({flower=1,star=2,life=3})[kind],
  x=({flower=1248,star=1616,life=1024})[kind]}
 S.target=target;S.attempts=0;seen=false;geometry=nil;minimumY=255
 S.actor_birth=nil;S.minimum_y=nil;S.geometry=nil
 routeAt=clock;creditAt=nil;pulseUntil=-1;phase('route',c)
end
local function launch(c,following,buttons)
 if not c.grounded or c.lastA then return {}end
 pulseUntil=clock+2;phase(following,c)
 local b=buttons or {};b.a=true;return b
end
local function defend(c)
 local e=c.enemy()
 return {b=not not(e and e.dx>0 and e.dx<44 and math.abs(e.y-c.y)<32 and c.grounded)}
end
local function rowGeometry(c,a)
 -- The used question block remains solid. Discover the actual row instead
 -- of assuming whether this build's authored block is at Y128 or Y144.
 local row
 for _,y in ipairs({144,128,160})do if solid(c,target.x+8,y)then row=y;break end end
 assert(row,'Cannot locate the revealed Flower support row')
 local left,right=target.x,target.x+16
 for _=1,12 do if not solid(c,left-8,row)then break end;left=left-16 end
 for _=1,12 do if not solid(c,right+8,row)then break end;right=right+16 end
 local function supported(x)return solid(c,x+8,208)or solid(c,x+8,224)end
 -- Build a ground runway, then choose direction BEFORE the native launch.
 -- IcMoveDir cannot reverse an established air trajectory. Crossing the row
 -- boundary near the fixed arc's apex avoids jumping into its underside.
 local side='left'
 if not(supported(left-66)and supported(left-42))then
  assert(supported(right+50)and supported(right+26),'No safe ground runway beside Flower row')
  side='right'
 end
 return {row=row,left=left,right=right,side=side,
  stage=side=='left'and left-66 or right+50,
  launch=side=='left'and left-42 or right+26,
  sign=side=='left'and 1 or -1,item_x=a.x}
end

local function decide(c,ordinary)
 local power=c.r('IcPower')
 local aim=target.x-5
 local a=item(c,target.id)
 if a and not seen and math.abs(a.x-target.x)<=40 then
  seen=true;S.actor_birth={actor=a,player=snapshot(c)}
 end
 if seen then
  local credited=target.kind=='flower'and power>=2 or
   target.kind=='star'and c.r('StarInvincibleTimer')>0 or
   target.kind=='life'and c.r('NumberofLives')>baselineLives
  if credited and not creditAt then
   creditAt=clock;S['observed_'..target.kind]=snapshot(c);phase('post-credit',c)
  end
 end
 if creditAt then
  if target.kind=='flower'and power<2 then fail('Flower tier lost during the post-credit hold',c)end
  if target.kind=='life'and c.r('NumberofLives')<=baselineLives then fail('Life credit lost during the post-credit hold',c)end
  if clock-creditAt>=25 then
   S['post25_'..target.kind]=snapshot(c)
   if target.kind=='flower'then chooseTarget('star',c);return ordinary end
   phase('complete',c);S.complete=snapshot(c);return {}
  end
  return defend(c)
 end
 if clock-routeAt>1500 then fail('Finite '..target.kind..' route bound',c)end
 if target.kind=='flower'and power==0 then fail('Lost the earned parka before Flower',c)end
 if c.variant==1 and target.kind=='flower' and S.phase=='route' then
  if not S.nana_pipe_jump and c.grounded and not c.lastA
      and c.y==112 and c.x>=752 and c.x<=758 then
   -- A fresh jump from the pipe keeps the jump hammer active on descent.
   -- Walking off the pipe falls into the enemy pair in the Hard replay.
   S.nana_pipe_jump=snapshot(c);S.nana_pipe_jump.enemies={}
   for i=0,5 do
    local id,flag=c.r('Enemy_ID',i),c.r('Enemy_Flag',i)
    if id<0x15 and flag>0 and flag<128 then
     local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
     S.nana_pipe_jump.enemies[#S.nana_pipe_jump.enemies+1]={id=id,x=x,y=c.r('Enemy_Y_Position',i)}
    end
   end
  end
  if S.nana_pipe_jump and not S.nana_pipe_land then
   local age=clock-S.nana_pipe_jump.update
   if c.grounded and age>4 then S.nana_pipe_land=snapshot(c)
   else return {right=true,a=age<2}end
  end
 end
 minimumY=math.min(minimumY,c.y);S.minimum_y=minimumY
 if seen and a then
  if target.kind=='flower'then
   if not geometry then
    if a.state<128 then return defend(c)end
    geometry=rowGeometry(c,a);S.geometry=geometry;S.flower_geometry=geometry;phase('flower-stage',c)
   end
   if S.phase=='flower-stage'then
    if floor(c)and math.abs(c.x-geometry.stage)<=2 then phase('flower-settle',c);return {}end
    return moveToward(c,geometry.stage,2)
   elseif S.phase=='flower-settle'then
    if floor(c)and clock-phaseAt>=24 and still>=3 then phase('flower-run',c)end
    return {}
   elseif S.phase=='flower-run'then
    local reached=geometry.sign==1 and c.x>=geometry.launch or geometry.sign==-1 and c.x<=geometry.launch
    if reached and floor(c)then
     S.flower_launch=snapshot(c)
     return launch(c,'flower-jump',direction(geometry.sign))
    end
    return direction(geometry.sign)
   elseif S.phase=='flower-jump'then
    if c.grounded and clock-phaseAt>4 then
     if c.y+32<=geometry.row+2 then phase('flower-walk',c)
     else
      S.row_attempts=(S.row_attempts or 0)+1
      if S.row_attempts>=4 then fail('Flower row crossing did not land above its actual support',c)end
      phase('flower-stage',c)
     end
    end
    local b=direction(geometry.sign);b.a=clock<pulseUntil;return b
   elseif S.phase=='flower-walk'then return moveToward(c,a.x-4,2)end
  else
   if target.kind=='star' and c.variant==1 then
    S.star_path=S.star_path or {}
    if #S.star_path<12 and (not S.star_path[#S.star_path] or clock-S.star_path[#S.star_path].update>=24)then
     S.star_path[#S.star_path+1]={update=clock,x=c.x,y=c.y,actor=a}
    end
    -- The first bounce peaks high above the brick and drops farther right.
    -- Settle ahead of it, then jump straight up into the descending Star.
    if S.star_intercept_jump and clock-S.star_intercept_jump.update<42 then
     return {a=clock<pulseUntil}
    end
    if not S.star_intercept_jump and a.x<target.x+80 then
     if not S.star_intercept_stop then
      if c.x<target.x+51 then return {right=true}end
      S.star_intercept_stop=snapshot(c)
     end
     if a.state>=128 and a.x>=target.x+48 and a.y>=110
        and math.abs(a.x-c.x-6)<=13 and c.grounded and not c.lastA then
      S.star_intercept_jump=snapshot(c)
      return launch(c,'star-intercept',{})
     end
     return defend(c)
    end
   end
   -- Star and 1-UP leave their source block. Use the same physically moving
   -- actor catch as the first Mushroom; jump only from a fresh grounded edge.
   local b=moveToward(c,a.x-4,6)
   if c.grounded and not c.lastA and a.y<c.y-12 and math.abs(a.x-c.x)<40 then
    pulseUntil=clock+2
   end
   b.a=clock<pulseUntil;return b
  end
 end
 if seen then return {}end -- Await the actual credit; disappearance alone is insufficient.
 if S.phase=='route'then
  if c.x<target.x-80 then return ordinary end
  phase('approach',c)
 end
 if S.phase=='approach'then
  if not floor(c)then
   -- Walk off an accidentally reached row before attempting its underside.
   return moveToward(c,target.x-96,2)
  end
  if c.x<aim-14 then return {right=true}end
  if c.x>aim+14 then return {left=true}end
  phase('brake',c);return {}
 elseif S.phase=='brake'then
  if not floor(c)then phase('approach',c);return {}end
  if clock-phaseAt>=24 and still>=3 then
   local leftOfBlock=target.kind=='life' and 7 or 10
   if c.x>=target.x-leftOfBlock and c.x<=target.x+1 then
    S.attempts=S.attempts+1
    if S.attempts>8 then fail('Bounded '..target.kind..' head attempts exhausted',c)end
    S.last_bump=snapshot(c)
    return launch(c,'bump',{})
   end
   S.nudge=c.x<aim and 1 or -1;phase('nudge',c)
  end
  return {}
 elseif S.phase=='nudge'then
  if clock-phaseAt>=2 then phase('brake',c);return {}end
  return direction(S.nudge)
 elseif S.phase=='bump'then
  if clock-phaseAt>70 and c.grounded then phase('approach',c)end
  return {a=clock<pulseUntil}
 end
 return ordinary
end

return function(c)
 local ordinary=base(c) -- Preserve every original input-poll prefix decision.
 if c.char~=20 or c.world~=0 or c.level~=0 then return ordinary end
 clock=assert(c.update,'Supply the completed Main decision clock')
 baselineLives=baselineLives or c.r('NumberofLives')
 if not target then
  if c.r('IcPower')<1 then return ordinary end
  S.observed_mushroom=snapshot(c)
  chooseTarget(mode=='life'and'life'or'flower',c)
 end
 if S.phase=='complete'then return {}end
 if lastClock==clock then return cached end
 lastClock=clock
 if previousX==c.x then still=still+1 else still=0 end;previousX=c.x
 cached=decide(c,ordinary)
 return cached
end
