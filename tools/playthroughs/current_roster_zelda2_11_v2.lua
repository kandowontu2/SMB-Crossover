-- Controller-only cast acknowledgement around the unchanged retained route.
-- A one-poll Select during the first pickup previously left JUMP uncast.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/current_roster_zelda2_11_v1.lua'))
local castPoll=0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or (c.r('Z2LearnedSpells')&2)==0 then return b end
 b.select=false
 if (c.r('Z2ActiveSpells')&2)~=0 then return b end
 if c.r('GuestPowerupActive')~=0 or c.r('TimerControl')~=0 or c.r('GamePauseStatus')~=0 then return b end
 if (c.r('Z2Selection')&7)~=1 then return b end
 -- Eight bounded real presses with releases; stop as soon as native cast wins.
 castPoll=castPoll+1
 if castPoll<=128 then b.select=(castPoll-1)%16<8 end
 return b
end
