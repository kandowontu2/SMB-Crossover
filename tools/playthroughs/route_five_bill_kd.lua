-- Controller-only discovery, with actual Bill/Lance and Easy-mode guards.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/scc38d_bill_lance.lua'))
local best,stage,lastProgress=0,'',0
return function(c)
 assert(c.r('SelectedCharacter')==3 and c.r('BillVariant')==ROSTER_CONFIG.variant,'Actual Bill/Lance menu identity')
 assert(c.r('CrossoverBehaviorVersion')==0,'Actual Easy behavior')
 local key=c.world..'-'..c.level..'-'..c.area
 if key~=stage then stage=key;best=c.x;lastProgress=c.poll end
 if c.x>best+8 then best=c.x;lastProgress=c.poll end
 assert(c.poll-lastProgress<1000,'Bounded Bill navigation stall at '..key..' X'..c.x..' Y'..c.y)
 return prior(c)
end
