-- Crouched beam matches the low Cheep while on the real bank under a roof.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_lastwinged.lua'))
local started=nil
local log=assert(io.open(ROSTER_CONFIG.out..'exit-enemies.csv','w'))
log:write('poll,slot,id,flag,x,y,state,hp\n')
return function(c)
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2870 then
  for i=0,5 do log:write(table.concat({c.poll,i,c.r('Enemy_ID',i),c.r('Enemy_Flag',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_State',i),c.r('MmEnemyHP',i)},',')..'\n')end
  log:flush()
  if started==nil and c.grounded then started=c.poll end
  if started and c.poll-started<32 then return {down=true,b=c.poll%8<3}end
  if c.x>=2970 and c.grounded and c.y<=112 then return {right=true}end
 end
 return base(c)
end
