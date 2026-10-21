-- Samus/Bill/Lance candidate discovery. No emulated memory writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/roster_policy.lua'))
local initialUpgrade=false
local phase='approach'
local jumpAge=0
local holdA,cooldown=0,0
local function finish(b,c)
 if cooldown>0 then cooldown=cooldown-1 end
 if b.a and holdA==0 and cooldown==0 then holdA=32 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end end
 return b
end
return function(c)
 local b=travel(c)
 local e=c.enemy()
 -- Standing muzzles pass above the short enemies. Stop and use the native
 -- prone/crouch muzzle before the enemy reaches contact range.
 if e and e.dx>0 and e.dx<112 and math.abs(e.y-c.y)<32 and c.grounded then
  holdA=0
  return {down=true,b=c.poll%12<5}
 end
 if c.char==2 and c.r('SmBall')~=0 then
  -- Never strand a controller candidate in Morph Ball at a pipe.
  b.up=c.poll%2==0;b.down=false;b.a=false
 end
 -- The first ordinary mushroom is a real native pickup, collected through
 -- head contact and pursuit. Other upgrade coverage uses separate arenas.
 if c.world~=0 or c.level~=0 or initialUpgrade then return finish(b,c)end
 if c.status>0 then initialUpgrade=true;return finish(b,c)end
 if phase=='approach' and c.x<320 then return finish(b,c)end
 b={}
 if phase=='approach' then
  b.right=c.x<330;b.left=c.x>334
  if c.x>=330 and c.x<=334 and c.grounded then phase='bump';jumpAge=0 end
 elseif phase=='bump' then
  b.a=jumpAge<30;jumpAge=jumpAge+1
  b.right=c.x<330;b.left=c.x>334
  if jumpAge>65 and c.grounded then jumpAge=0 end
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then phase='collect' end end
 elseif phase=='collect' then
  local px,py
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)
  end end
  if not px then phase='bump';jumpAge=0;return finish(b,c)end
  b.right=c.x<px-5;b.left=c.x>px+5
  if py<c.y-10 and c.grounded then b.a=not c.lastA end
 end
 if e and math.abs(e.dx)<90 then
  b.b=c.poll%7==0
  if c.char==3 then b.down=c.grounded end
  if math.abs(e.dx)<24 and c.grounded then b.a=not c.lastA;b.down=false end
 end
 return finish(b,c)
end
