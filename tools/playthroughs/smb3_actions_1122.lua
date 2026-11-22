-- Normal inputs after both natural pickup checkpoints have completed.
local acquire=assert(SMB3_ACTION_ACQUIRE)
local S={phase='acquire',requested=assert(C.action),target=C.target_suit,changes={}}
SMB3_ACTION_STATE=S
local function change(c,p)
 S.phase=p;S.phase_motor=c.motor
 S.changes[#S.changes+1]={phase=p,update=c.update,motor=c.motor,x=c.x,y=c.y}
 assert(#S.changes<=16,'Finite SMB3 action phases')
end
return function(c)
 if not S.acquired then return acquire(c)end
 assert(c.r('M3Form')==S.target,'Naturally earned action form remains owned')
 if S.phase=='acquire'then change(c,'release-controls')end
 if S.phase=='release-controls'then
  if c.r('M3Growth')~=0 or c.r('M3Poof')~=0 or not c.grounded
     or c.r('M3Previous')&192~=0 then return {}end
  S.input={update=c.update,motor=c.motor,x=c.x,y=c.y,previous=c.r('M3Previous')}
  if S.requested=='Tanooki'then change(c,'enter-stone');return {down=true,b=true}
  elseif S.requested=='Frog'then change(c,'frog-hop');return {right=true}
  else change(c,'press-B');return {b=true}end
 elseif S.phase=='press-B'then
  assert(c.motor-S.phase_motor<12,'Actual fresh B is consumed within bounded input polls')
  if S.throw or S.tail then change(c,'observe-action');return {}end
  return {b=true}
 elseif S.phase=='enter-stone'then
  assert(c.update-S.input.update<100,'Native queued stone transformation completes')
  if S.stone and c.motor-S.stone.motor>=4 then
   S.exit_input={update=c.update,motor=c.motor};change(c,'release-stone');return {}
  end
  return {down=true,b=true}
 elseif S.phase=='frog-hop'then
  if c.motor-S.input.motor>=12 or c.x-S.input.x>=20 then change(c,'observe-action');return {}end
  return {right=true}
 end
 return {}
end
