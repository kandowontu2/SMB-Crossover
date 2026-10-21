-- Read-only encounter timing after the camera hold: advance far enough to
-- spawn the lower Goombas, then let them pass beneath the safe block row.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_bass_v34_policy.lua'))
local done,age,quiet,saw=false,0,0,false
return function(c)
 local b=prior(c)
 if c.char==1 and c.world==1 and c.level==0 and c.x>=1280 and c.x<1340
  and c.grounded and c.y<=128 and not done then
  age=age+1
  local below=false
  for i=0,5 do
   local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<0x15 and id~=13 and state<32
    and not(id==6 and state>=2)and x>c.x-32 and x<c.x+220
    and c.r('Enemy_Y_Position',i)>=c.y+32 then below=true end
  end
  saw=saw or below;quiet=below and 0 or quiet+1
  if(age>=120 and saw and quiet>=16)or(age>=300 and not saw)then
   done=true;print('MM34 lower row clear '..c.poll)
  else return{b=c.poll%8<3}end
 end
 return b
end
