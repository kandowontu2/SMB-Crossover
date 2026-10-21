-- Ordinary stage-local input reuse, followed by a mandatory fixed coldboot
-- proof. No emulated writes. The current partial room uses live navigation.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=assert(dofile(root..'/tools/playthroughs/scrooge32_water_pogo_policy.lua'))
ROSTER_CONFIG.policyAllModes=true
local reference={}
for line in io.lines(root..'/build/roster-through-2-2/mls-v32-scrooge-22-exit-tail-a-12-v0-mmc3/inputs.csv')do
 local _,f,m=line:match('^(%d+),(%d+),(%d+)$')
 if f then reference[tonumber(f)]=tonumber(m)end
end
local entries={['0-1']=4303,['0-2']=7957,['0-3']=10481,['1-0']=13046,['1-1']=16560}
local anchor,lastStage,firstStage,initialized
local out=assert(io.open(ROSTER_CONFIG.out..'scrooge-stage-reference.csv','w'))
out:write('frame,poll,stage,anchor,referenceFrame,mask\n')
local function buttons(mask)
 local b={}
 for _,v in ipairs({{'right',1},{'left',2},{'down',4},{'up',8},{'start',16},{'select',32},{'b',64},{'a',128}})do
  if(mask&v[2])~=0 then b[v[1]]=true end
 end
 return b
end
return function(c)
 local key=c.world..'-'..c.level
 if not initialized then initialized=true;if c.x>64 then firstStage=key end end
 if key~=lastStage then lastStage=key;anchor=nil end
 if key~=firstStage and entries[key]then
  if not anchor and c.r('OperMode')==1 and c.r('OperMode_Task')==3 and c.r('GameEngineSubroutine')==8 then anchor=c.frame end
  if anchor then
   local source=entries[key]+c.frame-anchor
   local mask=reference[source]
   if mask then out:write(table.concat({c.frame,c.poll,key,anchor,source,mask},',')..'\n');return buttons(mask)end
  end
 end
 return normal(c)
end
