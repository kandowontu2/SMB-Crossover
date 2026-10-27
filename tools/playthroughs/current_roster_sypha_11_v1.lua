-- Controller-only Sypha walking priority. The generic 2/8-poll B pulse
-- otherwise restarts her genuine 16-update grounded staff animation.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
return function(c)
 local b=base(c)
 if c.char~=5 or c.r('Cv3Variant')~=2 or c.world~=0 or c.level~=0 then return b end
 local e=c.enemy()
 -- A real forward nearby foe can need the staff. A target behind the
 -- player/camera must not turn ordinary walking into repeated idle casts.
 -- Native right-facing melee: X+14,width20; enemy overlap adds15.
 -- Its Y+12,height8 rectangle accepts enemy origins in [-11,19].
 -- Do not stop for the source's immune Beetle/Bullet or excluded Podoboo.
 local near=e and e.dx>0 and e.dx<34 and e.x>=c.camera
  and e.y-c.y>=-11 and e.y-c.y<20 and e.id<0x15
  and e.id~=2 and e.id~=8 and e.id~=12
 b.b=not not(b.b and near)
 return b
end
