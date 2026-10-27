-- Input-only Easy Ryu1-1 wall-top retry; original shared controller stays exact.
local root=assert(ROSTER_CONFIG.root)
local base=assert(dofile(root..'/tools/playthroughs/link_simon_ryu_policy.lua'))
local phase,started='release',nil
return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='ryu'or ROSTER_CONFIG.mode_value~=0 or c.char~=10
    or c.world~=0 or c.level~=0 or c.areaType~=1 or c.x<512
    or c.yHigh~=1 or c.r('XgWall')==0 or c.state==3 then
  phase,started='release',nil;return b
 end
 local face=c.r('PlayerFacingDir')
 local probe=c.x+(face==1 and 21 or-5)
 -- Literal source RyuWallJump top probe: X+21/-5, Y+3 must be air.
 if c.block(probe,c.y+3)~=0 then phase,started='release',nil;return b end
 if not started then started=c.poll end
 local previous=c.r('RgPreviousButtons')&128
 local saved=c.r('PreviousA_B_Buttons')&128
 local consumed=c.r('A_B_Buttons')&128
 local press=false
 if phase=='release'then
  -- Poll alternation can miss the actual movement/weapon-history readers.
  -- Retain release until both source history owners and current consumed A
  -- genuinely clear, with more than one poll of release held.
  if c.poll-started>=2 and previous==0 and saved==0 and consumed==0 then
   phase,started='press',c.poll;press=true
  end
 else
  press=true
  -- If a press crossed a mid-Main NMI and never created a movement edge,
  -- rearm through the same real release owners. No state is fabricated.
  if c.poll-started>=8 and c.r('XgFresh')&128==0 then
   phase,started='release',c.poll;press=false
  end
 end
 return{right=face==1,left=face==2,up=true,a=press}
end
