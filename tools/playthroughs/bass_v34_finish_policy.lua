-- Keep the34b dry navigation and the ordinary-buster wait used by the
-- independently verified32 route before the final water enemy.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v34_late_dash.lua'))
local age,done=0,false
return function(c)
 if c.char==9 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2790 and c.x<2825 and not done then
  age=age+1
  if age<=120 then return{b=age%8<4}end
  done=true;print('BASS34 final fish burst '..c.poll)
 end
 return prior(c)
end
