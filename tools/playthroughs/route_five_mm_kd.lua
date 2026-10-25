-- Ordinary inputs for the current Easy route. Fire into a blocking brick
-- instead of repeating an impossible jump in the one-tile underground notch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_bass_v34_policy.lua'))
local best,stage,lastProgress=0,'',0
return function(c)
 local key=c.world..'-'..c.level..'-'..c.area
 if key~=stage then stage=key;best=c.x;lastProgress=c.poll end
 if c.x>best+8 then best=c.x;lastProgress=c.poll end
 assert(c.poll-lastProgress<1000,'Bounded navigation stall at '..key..' X'..c.x..' Y'..c.y)
 local b=prior(c)
 local t=c.block(c.x+24,c.y+14)
 if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 then b.b=c.poll%10<4 end
 return b
end
