-- Hold above the late floor actor and aim down before the spring approach.
-- Real controller inputs; observer below only reads game state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_normal_prone_v2.lua'))
local passed=false
local log=assert(io.open(ROSTER_CONFIG.out..'spring-enemies.csv','w'))
log:write('poll,playerX,playerY,slot,id,flag,x,y,state,hp\n')
return function(c)
 if c.char==3 and c.world==1 and c.level==0 and c.x>=2810 and c.x<2970 then
  local danger=false
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   log:write(table.concat({c.poll,c.x,c.y,i,id,flag,x,y,st,c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},',')..'\n')
   if flag>0 and flag<128 and st<32 and id<=6 and y>=144 and x>c.x-8 and x<c.x+112 then danger=true end
  end
  log:flush()
  if not passed and c.x>=2866 then
   if danger then return {down=true,b=c.poll%8<3}end
   passed=true
  end
 end
 return base(c)
end
