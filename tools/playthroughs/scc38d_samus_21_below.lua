-- An intervening brick bank can catch the paused leap above the floor enemies.
-- Remain on that real support until both Goombas have walked beneath/behind;
-- resuming an automatic gap jump would descend directly into the pair.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_landing.lua'))
return function(c)
 if c.world==1 and c.level==0 and c.x>=480 and c.x<720 and c.grounded and c.y<160 then
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   if flag>0 and flag<128 and id<0x15 and id~=13 and st<0x20 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if x-c.x> -24 and x-c.x<160 and c.r('Enemy_Y_Position',i)>c.y+40 then
     return {b=c.poll%8<3}
    end
   end
  end
 end
 return base(c)
end
