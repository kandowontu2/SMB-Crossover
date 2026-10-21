-- Drop to actual near-side floor before the64px main2-1 pit.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-n.lua'))
local phase,age,off='drop',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-21-pit-control.csv','w'))
f:write('poll,phase,x,y,state,power,off\n')
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==1 and c.level==0 and c.x>=1360 and c.x<1580 and phase~='done' then
  if c.poll%4==0 then f:write(table.concat({c.poll,phase,c.x,c.y,c.state,c.status,off},',')..'\n');f:flush()end
  if phase=='drop' then
   if c.grounded and c.y>=160 and c.x>=1430 then phase='lip';return{}end
   return{right=c.x<1452,left=c.x>1455}
  elseif phase=='lip' then
   if c.grounded and c.x>=1460 and off>=6 then phase='cross';age=0;print('MM-S2 main2-1 near-edge jump '..c.poll..' X'..c.x);return{right=true,a=true}end
   return{right=c.x<1462}
  else
   age=age+1
   if c.grounded and c.x>=1530 then phase='done';print('MM-S2 main2-1 pit landed '..c.poll..' X'..c.x)end
   return{right=true,a=age<64}
  end
 end
 return b
end
