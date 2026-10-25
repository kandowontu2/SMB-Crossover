-- Read-only controller discovery. Clear the low brick ceiling before the
-- first underground gap; otherwise Bill's jump hits it and falls short.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/bill_powered_route_aa.lua'))
local phase,age,target='approach',0,nil
local log=assert(io.open(ROSTER_CONFIG.out..'gap-roof.csv','w'));log:write('poll,phase,x,y,target,roof\n')
return function(c)
 if c.world==0 and c.level==1 and c.x>=1232 and c.x<1380 and phase~='done' then
  c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
  if not target then
   for wx=1248,1376,16 do if c.block(wx,208)==0 then target=wx-12;break end end
   target=target or 1268
  end
  log:write(table.concat({c.poll,phase,c.x,c.y,target,c.block(c.x+8,144)},',')..'\n');log:flush()
  if phase=='approach' then
   if c.grounded and c.x>=target and c.x<=target+3 then phase='clear';age=0
   else return {right=c.x<target,left=c.x>target+3,b=c.poll%8<3}end
  end
  if phase=='clear' then
   age=age+1
   if age>=90 then phase='jump';age=0 end
   return {up=true,b=c.poll%8<3}
  end
  if phase=='jump' then
   age=age+1
   if c.grounded and age>8 and c.x>target+35 then phase='done'
   else return {right=true,a=age<56,b=c.poll%8<3,up=c.y>130}end
  end
 end
 return base(c)
end
