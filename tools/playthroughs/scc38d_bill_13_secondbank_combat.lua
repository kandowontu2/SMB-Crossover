-- Ordinary lower-bank firing while the next high-bank Goomba descends.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_13_lowerbank_combat.lua'))
local ready,done=false,false
local log=assert(io.open(ROSTER_CONFIG.out..'bank-enemies.csv','w'));log:write('poll,slot,id,flag,x,y,state,hp\n')
return function(c)
 if c.char==3 and c.world==0 and c.level==2 and c.x>=1080 and c.x<1320 and not done then
  for i=0,5 do log:write(table.concat({c.poll,i,c.r('Enemy_ID',i),c.r('Enemy_Flag',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_State',i),c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},',')..'\n')end;log:flush()
  if not ready then
   if c.grounded and c.x>=1138 and c.x<=1141 then ready=true end
   return {right=c.x<1138,left=c.x>1141,b=false}
  end
  local active=false
  for i=0,5 do
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==6 and c.r('Enemy_State',i)<32 and x>=1100 and x<1320 then active=true end
  end
  if active then
   if c.r('PlayerFacingDir')~=1 then return {right=true}end
   return {down=true,b=c.poll%8<3}
  end
  done=true
 end
 return base(c)
end
