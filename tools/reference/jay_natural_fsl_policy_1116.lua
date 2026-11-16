-- Source-only ordinary controls. Current owning facade supplies observations.
local P={};P.__index=P
function P.new(kind)
 assert(kind=='flower'or kind=='star'or kind=='life')
 return setmetatable({kind=kind,clock=0,phase='opening',at=0,hold=0,firstM=false,credit=false,lastA=false},P)
end
function P:change(phase)self.phase=phase;self.at=self.clock end
function P:collect(kind)
 if kind=='mushroom'and self.kind=='flower'and not self.firstM then
  self.firstM=true;self:change('M-resume')
 elseif kind==self.kind then self.credit=true;self:change(kind=='flower'and'earned-attack'or'credited')end
end
local function platform(actors,left)
 for _,a in ipairs(actors)do if a.flag==1 and a.id==37 and a.x==left then return a end end
end
function P:decide(s,actors)
 self.clock=self.clock+1
 if s.engine~=8 then return 0 end
 local x,y,g=s.x,s.y,s.grounded
 local item,enemy
 for _,a in ipairs(actors)do
  if a.flag~=0 and a.id==46 then item=a end
  if a.flag>0 and a.flag<128 and a.id==6 and a.state&32==0 and a.x>x and a.x-x<140 and math.abs(a.y-y)<30 then
   if not enemy or a.x<enemy.x then enemy=a end
  end
 end
 local shot=enemy and self.clock%12<2 and 64 or 0
 local bits=0
 if self.phase=='opening'then
  local age=self.clock-1
  if age<60 then bits=age<4 and 0 or age<36 and 1 or age<52 and 129 or 1
  else self:change(self.kind=='flower'and'M-approach'or'first')end
 end
 if self.phase:sub(1,2)=='M-'and self.phase~='M-resume'then
  local lift=platform(actors,384)
  local boarded=lift and lift.contact==lift.slot and y+32==lift.y and g
  if self.phase=='M-approach'and x>=332 and g then self:change('M-park')end
  if self.phase=='M-park'and self.clock-self.at>=8 then self:change('M-reveal')end
  if item and(self.phase=='M-approach'or self.phase=='M-park'or self.phase=='M-reveal')then self:change('M-lift-approach')end
  if self.phase=='M-approach'then bits=1|shot
  elseif self.phase=='M-park'then bits=shot
  elseif self.phase=='M-reveal'then bits=(self.clock-self.at<18 and 128 or 0)|shot
  elseif self.phase=='M-lift-approach'then
   bits=(x<408 and 1 or 0)|shot
   if x>=408 and g then self:change('M-lift-wait');bits=shot end
  elseif self.phase=='M-lift-wait'then
   bits=shot
   if boarded then self:change('M-lift-ride')
   elseif lift and g and lift.y>=176 then self:change('M-lift-board');bits=bits|128 end
  elseif self.phase=='M-lift-board'then
   bits=(self.clock-self.at<18 and 128 or 0)|shot
   if boarded then self:change('M-lift-ride');bits=shot
   elseif g and self.clock-self.at>20 then self:change('M-lift-wait')end
  elseif self.phase=='M-lift-ride'then
   bits=shot
   if boarded and lift.y<=168 then self:change('M-lift-face');bits=2|shot end
  elseif self.phase=='M-lift-face'then
   bits=shot
   if boarded and s.source_flags&2~=0 and s.source_control&0x38==0 then self:change('M-collect');bits=130|shot end
  elseif self.phase=='M-collect'then
   bits=(item and x>item.x and 2 or 0)|shot
   if self.clock-self.at<18 then bits=bits|128 end
  end
 elseif self.phase=='M-resume'then
  if self.clock-self.at>=8 then self:change('first')end
  bits=0
 elseif self.phase=='first'or self.phase=='first-landing'or self.phase=='second-approach'or self.phase=='second-top'
  or self.phase=='third-board'or self.phase=='third-landing'or self.phase=='fourth-approach'
  or self.phase=='fourth-wait'or self.phase=='fourth-board'or self.phase=='fourth-landing'then
  local function jump(nextPhase,n)self:change(nextPhase);self.hold=self.clock+n end
  if self.phase=='first'and x>=400 and g then jump('first-landing',12)end
  if self.phase=='first-landing'and x>=505 and y==176 and g then self:change('second-approach')end
  if self.phase=='second-approach'and x>=568 and g then jump('second-top',14)end
  if self.phase=='second-top'and x>=625 and y==128 and g then jump('third-board',14)end
  local p3=platform(actors,688)
  if self.phase=='third-board'and self.clock>=self.hold and p3 and p3.contact==p3.slot and y+32==p3.y and g then jump('third-landing',14)end
  if self.phase=='third-landing'and x>=800 and y==176 and g then self:change('fourth-approach')end
  if self.phase=='fourth-approach'and x>=835 then self:change('fourth-wait')end
  local p4=platform(actors,880)
  if self.phase=='fourth-wait'and p4 and self.previousTop and p4.y>self.previousTop and p4.y>=155 then jump('fourth-board',14)end
  if p4 then self.previousTop=p4.y end
  if self.phase=='fourth-board'and self.clock>=self.hold and p4 and p4.contact==p4.slot and y+32==p4.y and g then jump('fourth-landing',14)end
  bits=(self.phase=='fourth-wait'and 0 or 1)|shot
  if self.clock<self.hold then bits=bits|128 end
  if self.phase=='fourth-landing'and x>=995 and y==176 and g then
   self:change(self.kind=='life'and'target-approach'or'gap1-approach');bits=1|shot
  end
 elseif self.phase=='gap1-approach'then
  bits=1|shot
  if x>=1082 and g then self:change('gap1');self.hold=self.clock+14;bits=bits|128 end
 elseif self.phase=='gap1'then
  bits=1|shot
  if self.clock<self.hold then bits=bits|128 end
  if x>=1150 and g then self:change(self.kind=='flower'and'target-approach'or'gap2-approach')end
 elseif self.phase=='gap2-approach'then
  bits=1|shot
  if x>=1360 and g then self:change('gap2');self.hold=self.clock+14;bits=bits|128 end
 elseif self.phase=='gap2'then
  bits=1|shot
  if self.clock<self.hold then bits=bits|128 end
  if x>=1450 and g then self:change('target-approach')end
 elseif self.phase=='target-approach'then
  local target=({flower=1244,star=1612,life=1020})[self.kind]
  bits=(x<target and 1 or x>target+2 and 2 or 0)|shot
  if x>=target and x<=target+2 and g then self:change('target-park');bits=shot end
 elseif self.phase=='target-park'then
  bits=shot
  if self.clock-self.at>=8 then self:change('target-reveal');bits=128|shot end
 elseif self.phase=='target-reveal'then
  bits=(self.clock-self.at<18 and 128 or 0)|shot
  if item then self:change('target-collect')
  elseif self.clock-self.at>64 and g then self:change('target-park')end
 elseif self.phase=='target-collect'then
  if item then
   if self.kind~='life'and item.state<128 then self.lastA=false;return shot end
   bits=(x<item.x-3 and 1 or x>item.x+4 and 2 or 0)|shot
   if g and not self.lastA then self.hold=self.clock+18 end
   if self.clock<self.hold then bits=bits|128 end
  else bits=0 end
 elseif self.phase=='earned-attack'then
  bits=enemy and enemy.x-x<110 and 0 or 1
  if self.clock%12<2 then bits=bits|64 end
 elseif self.phase=='credited'then bits=0 end
 self.lastA=bits&128~=0
 return bits
end
return P
