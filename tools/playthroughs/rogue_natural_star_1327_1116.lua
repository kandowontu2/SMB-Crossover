-- Independent genuine M prefix, authored1616 Star reveal, real mobile chase.
local phase='travel'
local hold=0
return function(c,stock,items)
 if stock=='tank'then return base(c)end
 if stock=='tank-credit'or stock=='star-credit'then return{}end
 local item
 for _,a in ipairs(items)do if a.id==46 and a.kind==2 then item=a end end
 if item then return{right=c.x<item.x-2,left=c.x>item.x+2,b=c.poll%7<3}end
 local action,vy,gravity=c.r('RdAction'),c.r('RdVY'),c.r('RdGravity')
 local ready=c.grounded and(action==0 or action==4 or(action==1 and vy<128 and gravity==0))
 if phase=='travel'and c.x>=1548 then phase='land'end
 if phase=='travel'then return base(c)end
 if phase=='land'then
  if c.x>=1567 and c.x<=1569 and c.y>=176 and ready then phase='align'end
  return{right=c.x<1567,left=c.x>1569,a=vy>=128,b=c.poll%7<3}
 elseif phase=='align'then
  if c.x>=1616 and c.x<=1618 and c.y>=176 and ready and(c.r('RdHeld')&128)==0 and(c.r('RdHit')&32)==0 and c.r('RdHurtClock')==0 then phase='bump';hold=48 end
  return{right=c.x<1616,left=c.x>1618,b=c.poll%7<3}
 elseif phase=='bump'then
  hold=math.max(hold-1,0)
  if hold==0 and ready and(c.r('RdHeld')&128)==0 then hold=48 end
  return{right=c.x<1616,left=c.x>1618,a=hold>0 or vy>=128,b=c.poll%7<3}
 end
 return{}
end
