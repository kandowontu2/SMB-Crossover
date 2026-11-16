-- Retained genuine first tank, then normal floor alignment and side mount.
local phase='travel'
local hold=0
return function(c,stock,items)
 if stock=='tank'then return base(c)end
 if stock=='tank-credit'or stock=='missile-credit'then return{}end
 local a
 for _,v in ipairs(items)do if v.id==46 and v.owner==2 and v.private==217 then a=v end end
 local action,vy,gravity=c.r('RdAction'),c.r('RdVY'),c.r('RdGravity')
 local ready=(action==0 or action==4 or(action==1 and vy<128 and gravity==0))and c.grounded
 if a then
  if phase~='mount-back'and phase~='mount-rise'and phase~='mount-cross'then phase='mount-back';hold=0 end
  if phase=='mount-back'then
   if c.x>=1195 and c.x<=1197 and c.y>=176 and ready and(c.r('RdHeld')&128)==0 then phase='mount-rise';hold=48;return{a=true,b=c.poll%7<3}end
   return{right=c.x<1195,left=c.x>1197,b=c.poll%7<3}
  elseif phase=='mount-rise'then
   if c.y<=112 and c.yHigh==1 then phase='mount-cross'end
   hold=math.max(hold-1,0)
   return{a=hold>0 or vy>=128,b=c.poll%7<3}
  else
   if c.y>=176 and ready then phase='mount-back';hold=0 end
   return{right=c.x<a.x-4,left=c.x>a.x+4,a=vy>=128,b=c.poll%7<3}
  end
 end
 if phase=='travel'and c.x>=1188 then phase='land'end
 if phase=='travel'then return base(c)end
 if phase=='land'then
  if c.x>=1199 and c.x<=1201 and c.y>=176 and ready then phase='align' end
  return{right=c.x<1199,left=c.x>1201,b=c.poll%7<3,a=vy>=128}
 elseif phase=='align'then
  if c.x>=1248 and c.x<=1250 and c.y>=176 and ready and(c.r('RdHeld')&128)==0 then phase='bump';hold=48 end
  return{right=c.x<1248,left=c.x>1250,b=c.poll%7<3}
 elseif phase=='bump'then
  hold=math.max(hold-1,0)
  if hold==0 and ready and(c.r('RdHeld')&128)==0 then hold=48 end
  return{right=c.x<1248,left=c.x>1250,a=hold>0 or vy>=128,b=c.poll%7<3}
 end
 return{}
end
