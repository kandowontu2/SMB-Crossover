-- Ordinary controller setup for the two64px rises in1-3. Bass's first jump
-- alone is too low; jump vertically and use the second edge before moving over
-- the higher cap. This policy never changes emulated state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v34_policy.lua'))
local phase,age,step='position',0,1
local offAge,quiet=0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==9 and c.world==0 and c.level==2 and c.x>=500 and c.x<752 and phase~='done'then
  local takeoff=step==1 and 524 or 604
  local landing=step==1 and 96 or 32
  if phase=='fightposition'then
   if c.x<568 then return{right=true}end
   if c.x>571 then return{left=true}end
   if not c.grounded then return{}end
   phase='fight';age=0;quiet=0
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
  end
  if phase=='fight'then
   local foe=false
   for i=0,5 do
    local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if f>0 and f<128 and id<0x15 and id~=13 and st<32
     and x>c.x-24 and x<c.x+224 then foe=true end
   end
   age=age+1;quiet=foe and 0 or quiet+1
   if age>=90 and quiet>=20 then step=2;phase='position';age=0;return{}end
   return{b=true}
  end
  if phase=='position'then
   if c.x<takeoff then return{right=true}end
   if c.x>takeoff+3 then return{left=true}end
   if not c.grounded or offAge<6 then return{}end
   phase='first';age=0
  end
  age=age+1
  if phase=='first'then
   if age>=20 then phase='release';age=0;return{}end
   return{a=true}
  elseif phase=='release'then
   if age>=6 then phase='second';age=0;return{a=true}end
   return{}
  elseif phase=='second'then
   if c.grounded and c.y<=landing and c.x>=(step==1 and 568 or 648)then
    if step==1 then phase='fightposition';age=0;return{}end
    phase='done';return{right=true}
   end
   return{a=age<34,right=c.y<=landing-4 or age>18}
  end
 end
 return prior(c)
end
