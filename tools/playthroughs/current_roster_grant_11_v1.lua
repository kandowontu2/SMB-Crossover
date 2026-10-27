-- Controller-only walking priority; repeated generic B pulses otherwise
-- keep restarting Grant's genuine 16-update grounded knife animation.
local root=assert(ROSTER_CONFIG.root)
local base=assert(dofile(root.."/tools/playthroughs/full_roster_policy_og.lua"))
local quietUntil=0

return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='grant'or ROSTER_CONFIG.mode_value~=1
    or c.char~=5 or c.variant~=1 or c.world~=0 or c.level~=0 then return b end
 local age=c.r('Cv3AttackAge')
 if age~=0 then quietUntil=c.poll+8 end
 local e=c.enemy()
 -- Right-facing knife: X+14, width12; source enemy overlap adds15.
 -- Y+12, height8 accepts enemy origins from Y-11 through Y+19.
 -- Beetle/Bullet are immune, Podoboo is excluded. A wall grip uses the
 -- source subweapon branch, not this ordinary knife admission.
 local near=e and e.dx>=0 and e.dx<26 and e.x>=c.camera
  and e.y-c.y>=-11 and e.y-c.y<20 and e.id<0x15
  and e.id~=2 and e.id~=8 and e.id~=12
 b.b=not not(b.b and near and b.right and not b.left
  and age==0 and c.poll>=quietUntil and c.r('Cv3Climb')==0)
 return b
end
