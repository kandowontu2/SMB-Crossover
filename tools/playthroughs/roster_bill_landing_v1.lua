-- Bill-only input successor. No emulated state writes or wall-frame exceptions.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local original=assert(dofile(root..'/tools/playthroughs/roster_samus_contra.lua'))
local retreatRow
local function solid(c,x,y)
 local t=c.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
end
local function landingRow(c,e)
 -- Corroborate ordinary floor across the retreat and the approach; never
 -- retreat toward a gap merely because Player_State says "air".
 local first=math.max(32,math.ceil((c.y+32)/16)*16)
 for y=first,224,16 do
  local supported=solid(c,e.x+8,y)
  for dx=-48,32,16 do supported=supported and solid(c,c.x+dx,y)end
  if supported then return y end
 end
end
return function(c)
 local b=original(c) -- Advance the unchanged parent's controller exactly once.
 if c.char~=3 or c.variant~=0 or c.world~=0 or c.level~=0 or c.engine~=8 then
  retreatRow=nil;return b
 end
 local e=c.enemy()
 if not e or e.id~=6 or e.state>=2 or math.abs(e.dx)>=112 then
  retreatRow=nil;return b
 end
 local falling=c.state==1 and c.vy>0 and c.vy<128
 if not retreatRow and falling and e.dx>0 and e.dx<64
  and e.y-c.y>=-8 and e.y-c.y<96 and c.x>c.camera+60 then
  retreatRow=landingRow(c,e)
 end
 if retreatRow and not c.grounded then
  if falling and c.x>c.camera+12 and solid(c,c.x-24,retreatRow)then
   -- Bill's neutral airborne input retains VX. Real Left supplies braking.
   return {left=true,b=false}
  end
  retreatRow=nil;return b
 end
 if c.grounded and math.abs(e.y-c.y)<32
  and solid(c,c.x+8,c.y+32)
  and c.block(c.x+(e.dx<0 and -12 or 24),c.y+24)==0 then
  retreatRow=nil
  local dir=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=dir then return {left=dir==2,right=dir==1,b=false}end
  -- A physical poll may repeat within one Main update. Wait for the real
  -- weapon consumer's history before changing the next B edge; no poll phase.
  return {down=true,b=(c.r('RgPreviousButtons')&64)==0}
 end
 retreatRow=nil
 return b
end
