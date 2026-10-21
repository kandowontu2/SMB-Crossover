-- Scan floor threats separately from the nearer Piranha.
-- Let the real short pipe catch the descending leap before its floor enemy;
-- then use a fresh A edge from that genuine raised support.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_aftergap_landing.lua'))
local hold=0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=1840 and c.x<2944 then
  if hold>0 then hold=hold-1;return {right=true,a=true,b=c.poll%8<3}end
  local e
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if flag>0 and flag<128 and id<0x15 and id~=13 and st<32 and x>=c.x and x-c.x<120 and y>c.y+24 then
    if not e or x<e.x then e={id=id,x=x,y=y,dx=x-c.x}end
   end
  end
  if e and e.id~=13 and e.dx>=0 and e.dx<120 and e.y>c.y+24 then
   if c.grounded and c.y<176 and not c.lastA then hold=31;return{right=true,a=true,b=c.poll%8<3}end
   local tile=c.block(c.x+8,216)
   if c.yHigh==1 and not c.grounded and c.vy<128 and tile~=0 and tile~=0x23 then
    if c.r('PlayerFacingDir')~=1 then return {right=true,b=true}end
    return {b=c.poll%8<3}
   end
  end
 end
 return base(c)
end
