-- Prone fire from actual floor before the late Goomba pair, ignoring airborne distractors.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_highplant_cross.lua'))
local done=false
local log=assert(io.open(ROSTER_CONFIG.out..'late-enemies.csv','w'));log:write('poll,slot,id,flag,x,y,state,hp\n')
return function(c)
 if c.char==3 and c.world==1 and c.level==0 and c.x>=2470 and c.x<2660 and not done and c.grounded then
  local active=false
  for i=0,5 do
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local id,flag,st,y=c.r('Enemy_ID',i),c.r('Enemy_Flag',i),c.r('Enemy_State',i),c.r('Enemy_Y_Position',i)
   log:write(table.concat({c.poll,i,id,flag,x,y,st,c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},',')..'\n')
   if flag>0 and flag<128 and id==6 and st<32 and y>=144 and x>c.x-32 and x<2750 then active=true end
  end;log:flush()
  if active then
   if c.r('PlayerFacingDir')~=1 then return {right=true}end
   return {down=true,b=c.poll%8<3}
  end
  done=true
 end
 return base(c)
end
