local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/roster_samus_contra.lua'))
local seen={}
local platforms=assert(io.open(ROSTER_CONFIG.out..'platforms.csv','w'));platforms:write('frame,slot,id,x,y,state\n')
local log=assert(io.open(ROSTER_CONFIG.out..'geometry.csv','w'));log:write('frame,x,y,state,camera,enemyId,enemyX,enemyY,enemyState\n')
return function(c)
 if c.world==0 and c.level==1 then
  if c.x>2050 and c.frame%4==0 then for i=0,5 do if c.r('Enemy_Flag',i)>0 then platforms:write(string.format('%d,%d,%d,%d,%d,%d\n',c.frame,i,c.r('Enemy_ID',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_State',i)))end end;platforms:flush()end
  local e=c.enemy()
  if c.frame%8==0 then log:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d\n',c.frame,c.x,c.y,c.state,c.camera,e and e.id or -1,e and e.x or -1,e and e.y or -1,e and e.state or -1));log:flush() end
  local interval=math.floor((c.x-1500)/64)
  if interval>=0 and interval<20 and not seen[interval] then
   seen[interval]=true
   local f=assert(io.open(ROSTER_CONFIG.out..'geometry-'..interval..'.png','wb'));f:write(emu.takeScreenshot());f:close()
   local f=assert(io.open(ROSTER_CONFIG.out..'blocks-'..interval..'.csv','w'))
   f:write('wx,y,tile\n')
   for x=math.floor(c.camera/16)*16,math.floor(c.camera/16)*16+256,16 do for y=32,224,16 do f:write(x..','..y..','..c.block(x,y)..'\n')end end
   f:close()
  end
 end
 return choose(c)
end

