-- Source-grounded pad hold: ordinary A must remain held through ascent.
-- Original CFC3/D002 gives84px when held; a32-controller-poll tap cuts it short.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v4.lua'))
return function(c)
 local b=route(c)
 local action=c.r('RdAction')
 if (action==1 or action==2 or action==6)and c.r('RdVY')>=128 then b.a=true end
 return b
end
