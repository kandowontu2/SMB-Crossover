-- Let Rygar land on the actual1-3 tree before approaching a nearby Koopa.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local follow=assert(dofile(root..'/tools/playthroughs/rygar_pipe_gap_dm.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'landing-response.csv','w'))
log:write('frame,poll,x,y,slot,kind,enemyX,enemyY,support\n')
return function(c)
 if c.world==0 and c.level==2 and not c.grounded and c.vy>0 and c.vy<128 then
  for i=0,5 do
   local kind,flag,state=c.r('Enemy_ID',i),c.r('Enemy_Flag',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local y=c.r('Enemy_Y_Position',i)
   local support=c.block(c.x+8,y+24)
   if flag>0 and flag<128 and kind<7 and state<32 and(kind~=6 or state<2)and x>=c.x and x-c.x<=48 and math.abs(y-c.y)<=36 and c.y+28>y+8 and support~=0 then
    log:write(table.concat({c.frame,c.poll,c.x,c.y,i,kind,x,y,support},',')..'\n');log:flush()
    return{b=c.frame%12<5}
   end
  end
 end
 return follow(c)
end
