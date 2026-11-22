-- Separate natural Mushroom/suit route. The pinned first-M controller is
-- injected unchanged; progress below is observer-owned Lua state, never RAM.
local base=assert(SMB3_UPGRADE_BASE)
local progress=assert(SMB3_UPGRADE_PROGRESS)
local mode=assert(SMB3_UPGRADE_MODE)
local target=SMB3_UPGRADE_TARGET
assert(mode=='mushroom' or mode=='mushroom-suit')
local phase,at,lastJump,hold='mushroom',0,-100,-1
local defense,defenseAt=false,0
local geometry=nil
local T={phase=phase,changes={},defense_jumps={}}
SMB3_UPGRADE_STATE=T
local function change(c,p)
 phase=p;at=c.update;T.phase=p
 T.changes[#T.changes+1]={phase=p,update=c.update,x=c.x,y=c.y,vx=c.vx}
 if #T.changes>24 then table.remove(T.changes,1)end
end
local function steer(c,goal,tolerance)
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local dx=goal-c.x;local lead=vx*vx/24+6;local band=tolerance or 3
 if vx>3 and dx<=lead then return {left=true}end
 if vx< -3 and -dx<=lead then return {right=true}end
 if dx>band then return {right=true}end
 if dx< -band then return {left=true}end
 if vx>0 then return {left=true}end
 if vx<0 then return {right=true}end
 return {}
end
local function defend(c)
 if defense then
  if c.grounded and c.update-defenseAt>4 then defense=false
  else return {right=true,a=c.update<hold}end
 end
 local e=c.enemy()
 if c.grounded and not c.lastA and c.update-lastJump>24 and e and e.dx>12 and e.dx<=64
    and e.y>=c.y-24 and e.y<=c.y+88 then
  defense=true;defenseAt=c.update;lastJump=c.update;hold=c.update+18
  T.defense_jumps[#T.defense_jumps+1]={update=c.update,x=c.x,y=c.y,enemy=e}
  assert(#T.defense_jumps<=8,'Bounded genuine defensive jumps')
  return {right=true,a=true}
 end
end
local function suitActor(c)
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i);local stamp=c.r('InvPickup',i)
  if flag>0 and flag<128 and c.r('Enemy_ID',i)==46 and c.r('InvPickupOwner',i)==17
     and stamp>=0xd2 and stamp<=0xd6 then
   return {slot=i,stamp=stamp,state=c.r('Enemy_State',i),
    x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
  end
 end
end
local function solid(c,x,y)
 local t=c.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function advanceRandom(bytes,n)
 local out={};for i=1,7 do out[i]=bytes[i]end
 for _=1,n do
  local carry=((out[1]>>1)~(out[2]>>1))&1
  for i=1,7 do
   local nextCarry=out[i]&1
   out[i]=(out[i]>>1)|(carry<<7);carry=nextCarry
  end
 end
 return out
end
local function readRandom(c)
 local out={};for i=0,6 do out[i+1]=c.r('PseudoRandomBitReg',i)end;return out
end
local function jumpDrawSteps(y,fraction)
 -- The authenticated native Super controller first applies the previous
 -- velocity, then starts a fresh -56/16 jump and adds held-A gravity1/16.
 -- Its first grounded update starts the jump without moving Y. The host's
 -- big-player head probe is origin+6; entering144..159 hits this real row.
 assert(y==176 and fraction>=0 and fraction<=255,'Exact grounded prediction origin')
 local velocity=-55
 for tick=2,16 do
  local sum=fraction+(velocity&15)*16
  fraction=sum&255;y=y+(velocity//16)+(sum>>8)
  if y+6>=144 and y+6<=159 then return tick end
  velocity=velocity+(velocity< -32 and 1 or 5)
 end
 error('Finite native jump-to-head prediction')
end
local function frozen(c)
 local out={x=c.x,y=c.y,vx=c.vx,state=c.r('Player_State'),frame=c.r('FrameCounter'),
  yfrac=c.r('M3Native::Player_YVelFrac'),yvel=c.r('M3Native::Player_YVel'),
  form=c.r('M3Form'),previous=c.r('M3Previous')}
 for i=0,5 do
  out['flag'..i]=c.r('Enemy_Flag',i);out['id'..i]=c.r('Enemy_ID',i)
  out['x'..i]=c.r('Enemy_X_Position',i);out['page'..i]=c.r('Enemy_PageLoc',i)
  out['y'..i]=c.r('Enemy_Y_Position',i);out['state'..i]=c.r('Enemy_State',i)
 end
 return out
end
local function pausedRandom(c,q)
 assert(c.r('GamePauseStatus')&1~=0,'Native pause remains active during finite RNG wait')
 local now=frozen(c);for k,v in pairs(q.frozen)do assert(now[k]==v,'Pause froze actual world field '..k)end
 local random=readRandom(c);local expected=advanceRandom(q.previous_rng,1)
 for i=1,7 do assert(random[i]==expected[i],'Exactly one native seven-byte LFSR rotation per paused GameLoop')end
 q.previous_rng=random;q.waited=c.update-q.paused_at
 assert(q.waited<=512,'Finite native pause/RNG selection limit')
 return random
end
local function scheduleUnpause(c,q,random)
 local predicted=advanceRandom(random,q.jump_steps)
 if predicted[3]%5+2~=target then return false end
 q.prediction={rng_before=random,draw=predicted[3],form=target,stamp=0xd0+target,
  rotations=q.jump_steps,read_before_update=c.update+q.jump_steps-1}
 q.unpause_input={update=c.update,x=c.x,y=c.y,frame=c.r('FrameCounter')}
 return true
end
if target then
 SMB3_UPGRADE_POLL=function(c)
  if (phase~='rng-wait'and phase~='rng-unpause')or T.rng.accepted then return nil end
  local q=T.rng
  if c.r('GamePauseStatus')&129~=1 or c.r('GamePauseTimer')~=0 then return {}end
  -- Re-read at the actual peripheral poll, including a poll in the short
  -- native return window. HpPauseCold later fixes the accepted source clock.
  if scheduleUnpause(c,q,readRandom(c))then
   q.poll_refreshes=(q.poll_refreshes or 0)+1
   q.last_poll={update=c.update,x=c.x,y=c.y,frame=c.r('FrameCounter')}
   if phase~='rng-unpause'then change(c,'rng-unpause')end
   return {start=true,a=true}
  end
  if phase=='rng-unpause'then
   q.canceled=(q.canceled or 0)+1;q.last_cancel={update=c.update,at_poll=true}
   q.prediction=nil;q.unpause_input=nil;change(c,'rng-wait')
  end
  return {}
 end
end
local function pauseControls(c)
 local q=assert(T.rng)
 if phase=='rng-pause-entry'then
  if c.r('GamePauseStatus')&1==0 then
   q.entry_waited=c.update-q.entry_update
   assert(q.entry_waited<=8,'Bounded wait for a real input poll and native Start acceptance')
   return {start=true}
  end
  local vx=c.vx>=128 and c.vx-256 or c.vx
  assert(c.grounded and c.y==176 and c.x>=1242 and c.x<=1246 and math.abs(vx)<=7
   and c.r('M3Form')==1 and c.r('M3Previous')&128==0,
   'Actually paused Super origin remains inside the authored head column with A released')
  q.jump_steps=jumpDrawSteps(c.y,c.r('M3Native::Player_YVelFrac'))
  q.frozen=frozen(c);q.previous_rng=readRandom(c);q.paused_at=c.update
  change(c,'rng-wait');return {}
 elseif phase=='rng-wait'then
  local random=pausedRandom(c,q)
  if c.r('GamePauseTimer')~=0 or c.r('GamePauseStatus')&128~=0 then return {}end
  if not scheduleUnpause(c,q,random)then return {}end
  change(c,'rng-unpause')
  return {start=true,a=true}
 elseif phase=='rng-unpause'then
  if c.r('GamePauseStatus')&1~=0 then
   -- A catch-up GameLoop can run before the next controller poll. Its
   -- old neutral input leaves the game paused but still advances RNG.
   assert(not q.accepted,'An accepted Start+A must actually unpause')
   local random=pausedRandom(c,q)
   if scheduleUnpause(c,q,random)then
    q.refreshed=(q.refreshed or 0)+1;return {start=true,a=true}
   end
   q.canceled=(q.canceled or 0)+1
   q.last_cancel={update=c.update,draw=q.prediction.draw}
   q.prediction=nil;q.unpause_input=nil
   change(c,'rng-wait');return {}
  end
  assert(q.accepted and c.update==q.accepted.before_update+1 and c.r('M3Fresh')&128~=0
   and c.r('M3Previous')&128~=0 and c.r('Player_State')==1,
   'Actual Start+A unpauses and starts a fresh native jump')
  lastJump=q.accepted.before_update;hold=lastJump+18
  q.unpaused={update=c.update,x=c.x,y=c.y,frame=c.r('FrameCounter')}
  change(c,'suit-bump')
  local b=steer(c,1244,2);b.a=c.update<hold;return b
 end
end
return function(c)
 local ordinary=base(c)
 if c.char~=17 or c.world~=0 or c.level~=0 then return ordinary end
 if c.r('M3Growth')~=0 or c.r('M3Poof')~=0 then return {}end
 if not progress.mushroom then
  if c.r('M3Form')==0 then return ordinary end
  return defend(c)or{}
 end
 if mode=='mushroom' or progress.suit then return defend(c)or{}end
 if progress.suit_collected then return defend(c)or{}end
 assert(c.r('M3Form')>=1,'Earned Super form lost before the authored suit block; Mushroom checkpoint remains valid')
 if phase=='mushroom'then change(c,'travel')end
 if phase=='travel'then
  if c.x<1152 then return defend(c)or ordinary end
  defense=false;change(c,'suit-brake')
 end
 if target and (phase=='rng-pause-entry'or phase=='rng-wait'or phase=='rng-unpause')then
  return pauseControls(c)
 end
 if target and T.rng and T.rng.prediction and not progress.suit_prepared then
  assert(c.update<=T.rng.prediction.read_before_update+3,'Predicted real head contact did not produce the authored suit')
 end
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local a=suitActor(c)
 if a and not geometry then
  local row
  for _,y in ipairs({144,128})do if solid(c,1256,y)then row=y;break end end
  -- The item appears before the bouncing block returns to the collision map.
  if not row then
   assert(c.update-lastJump<=55,'Bounced upgrade block did not settle')
   return steer(c,1244,2)
  end
  local left=1248
  for _=1,12 do if not solid(c,left-8,row)then break end;left=left-16 end
  geometry={row=row,left=left,stage=left-40,actor=a};T.geometry=geometry
  change(c,'suit-stage')
 end
 if geometry and a then
  if phase=='suit-stage'then
   if c.grounded and c.y>=160 and math.abs(c.x-geometry.stage)<=3 and math.abs(vx)<=3
      and a.state&128~=0 and not c.lastA then
    lastJump=c.update;hold=c.update+24;change(c,'suit-jump');return {right=true,a=true}
   end
   return steer(c,geometry.stage)
  elseif phase=='suit-jump'then
   if c.grounded and c.update-at>4 then
    if c.y+32<=geometry.row+2 then change(c,'suit-walk')
    else
     T.row_retries=(T.row_retries or 0)+1;assert(T.row_retries<=4,'Bounded actual suit-row crossing attempts')
     change(c,'suit-stage')
    end
   end
   local b=steer(c,a.x-4,2);b.a=c.update<hold;return b
  elseif phase=='suit-walk'then return steer(c,a.x-4,2)end
 end
 if phase=='suit-brake'then
  if vx>2 then return {left=true}end
  if vx< -2 then return {right=true}end
  change(c,'suit-position')
 end
 if phase=='suit-position'then
  if not(c.grounded and c.y>=160)then return steer(c,1208)end
  if math.abs(c.x-1244)<=2 and math.abs(vx)<=3 and not c.lastA and c.update-lastJump>24 then
   if target then
    assert(not T.rng and c.y==176 and c.r('M3Form')==1,
     'One stopped Super-form attempt targets the untouched authored suit block')
    T.rng={target=target,target_stamp=0xd0+target,entry_update=c.update,
     before_pause=frozen(c),rng_before_pause=readRandom(c)}
    T.head_attempts=1;change(c,'rng-pause-entry');return {start=true}
   end
   T.head_attempts=(T.head_attempts or 0)+1;assert(T.head_attempts<=8,'Bounded authored suit head attempts')
   lastJump=c.update;hold=c.update+18;change(c,'suit-bump');return {a=true}
  end
  return steer(c,1244,2)
 elseif phase=='suit-bump'then
  if c.update-at>75 and c.grounded then change(c,'suit-position')end
  local b=steer(c,1244,2);b.a=c.update<hold;return b
 end
 return {}
end
