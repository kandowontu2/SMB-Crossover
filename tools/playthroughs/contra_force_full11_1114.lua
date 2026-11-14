-- Ordinary source CF movement, crouch fire and fresh held jumps.
-- Live native terrain/enemies only; this route does not require powerups.
local jumpStart,releaseUntil=nil,0
local combatSlot,combatStart=nil,0
local lastX,lastY,still=nil,nil,0
local stair,stairPhase=1,'climb'
local stairs={{peak=2192,edge=2208,far=2240,finish=2304},
              {peak=2432,edge=2448,far=2480,finish=2544}}
local function air(t)return t==0 or t==0x23 or t==0x26 or t==0xc2 end
return function(c)
 local function solid(x,y)return not air(c.block(x,y))end
 local function aim(x,tol)return{right=c.x<x,left=c.x>x+(tol or 1)}end
 local function held(b)
  if b.a and not jumpStart then jumpStart=c.update end
  if jumpStart then
   if c.grounded and c.update>jumpStart+4 then
    jumpStart=nil;releaseUntil=c.update+4;b.a=false
   else b.a=c.update-jumpStart<44 end
  end
  if c.update<releaseUntil then b.a=false end
  return b
 end
 if lastX==c.x and lastY==c.y then still=still+1 else still=0 end
 lastX,lastY=c.x,c.y
 if c.world~=0 or c.level~=0 then return{},'post-1-1' end
 if c.areaType~=1 then return{},'unexpected-area','Unexpected non-overworld shortcut' end
 if still>=240 then return{},'travel','Stationary for240 controller decisions' end
 local b={right=true}
 local e=c.enemy()
 if e and e.id~=13 and e.dx>18 and e.dx<92 and math.abs(e.y-c.y)<36
    and c.grounded and c.update>=releaseUntil and not jumpStart and solid(c.x+8,c.y+33)then
  if combatSlot~=e.slot then combatSlot=e.slot;combatStart=c.update end
  local elapsed=c.update-combatStart
  if elapsed>=180 then return{},'combat','Enemy remains after180 original crouch-fire updates' end
  local settle=C.variant==2 and 0 or 4
  return{down=true,b=elapsed>=settle and(elapsed-settle)%8<2},'crouch-fire'
 end
 combatSlot=nil
 local s=stairs[stair]
 if s and c.x>=s.finish then stair=stair+1;stairPhase='climb';s=stairs[stair]end
 if s and c.x>=s.peak-20 and c.x<s.far and solid(s.peak+8,145)and not solid(s.edge+8,145)then
  if stairPhase=='climb'and c.y<=112 then stairPhase='land';jumpStart=nil;releaseUntil=c.update+4 end
  if stairPhase=='land'then
   b=aim(s.peak,1)
   if c.grounded and c.y<=112 and not c.heldA and c.update>=releaseUntil then
    stairPhase='cross';jumpStart=c.update;b={right=true,a=true}
   end
   return held(b),'stair-'..stair..'-'..stairPhase
  elseif stairPhase=='cross'then return held({right=true,a=true}),'stair-'..stair..'-cross' end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+32,math.min(feet-8,232))or solid(c.x+32,c.y+8)
 local gap=not solid(c.x+18,216)
 local danger=e and e.dx> -12 and e.dx<28 and math.abs(e.y-c.y)<48
 if c.grounded and not c.heldA and c.update>=releaseUntil and(obstacle or gap or danger or still>20)then b.a=true end
 if c.x>3060 then b.right=true end
 return held(b),'travel'
end
