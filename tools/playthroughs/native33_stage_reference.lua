-- Controller-only stage-local reuse of an earlier genuine native run.
-- This produces a new input CSV; it is never itself an accepted fixed proof.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/native33_finish_policy.lua'))
ROSTER_CONFIG.policyAllModes=true
local char=ROSTER_CONFIG.character
local folder=char==8 and 'mls-v24-luigi-proof-8-v0-mmc3' or 'mls-v24-mario-proof-0-v0-mmc3'
local reference={}
for line in io.lines(root..'/build/roster-through-2-2/'..folder..'/inputs.csv')do
 local _,f,m=line:match('^(%d+),(%d+),(%d+)$')
 if f then reference[tonumber(f)]=tonumber(m)end
end
local entries=char==8 and {['0-1']=3459,['0-2']=6450,['0-3']=8532,['1-0']=10530,['1-1']=13322}
 or {['1-0']=9781,['1-1']=13073}
local anchor,lastStage
local log=assert(io.open(ROSTER_CONFIG.out..'stage-reference.csv','w'))
log:write('frame,poll,stage,anchor,referenceFrame,mask\n')
local function buttons(mask)
 local b={}
 local names={{'right',1},{'left',2},{'down',4},{'up',8},{'start',16},{'select',32},{'b',64},{'a',128}}
 for _,v in ipairs(names)do if (mask & v[2])~=0 then b[v[1]]=true end end
 return b
end
return function(c)
 local stage=c.world..'-'..c.level
 if stage~=lastStage then lastStage=stage;anchor=nil end
 if entries[stage]then
  if not anchor and c.r('OperMode')==1 and c.r('OperMode_Task')==3 and c.r('GameEngineSubroutine')==8 then anchor=c.frame end
  if anchor then
   local source=entries[stage]+c.frame-anchor
   local mask=reference[source]
   if mask then
    log:write(table.concat({c.frame,c.poll,stage,anchor,source,mask},',')..'\n')
    return buttons(mask)
   end
  end
 end
 return base(c)
end
