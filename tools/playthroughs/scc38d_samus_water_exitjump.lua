-- Fresh jump from actual late lower-bank landing; ordinary controls only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_lastwinged.lua'))
local started=nil
return function(c)
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2870 and c.x<2970 then
  if started==nil and c.grounded and(c.r('PreviousA_B_Buttons')&128)==0 then started=c.poll end
  return {right=true,b=c.poll%8<3,a=started~=nil and c.poll-started<32}
 end
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2970 and c.grounded and c.y<=112 then return {right=true}end
 return base(c)
end
