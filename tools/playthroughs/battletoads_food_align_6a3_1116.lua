 if food.phase=='mushroom'then food.phase='mushroom-align';food.alignSince=guestReturns end
 if food.phase=='mushroom-align'then
  assert(guestReturns-food.alignSince<550,'Bounded directed first-question alignment')
  buttons={right=c.x<327,left=c.x>330}
  local e=c.enemy();if e and e.dx>0 and e.dx<48 then buttons.b=guestReturns%32<2 end
  if c.x>=327 and c.x<=330 then buttons={}
   if c.grounded and c.y==176 and c.vx==0 and not c.lastA then food.settle=(food.settle or 0)+1 else food.settle=0 end
   if food.settle>=6 then
    food.phase='mushroom-head';food.headAt=guestReturns;food.headRequest=state()
    food.authored_tile=c.block(336,144);assert(food.authored_tile~=0,'Authored first question present');buttons={a=true}
   end
  end
  return
 elseif food.phase=='mushroom-head'then
  local a=target()
  if a then food.phase='mushroom-collect';food.collectAt=guestReturns;buttons={};return end
  buttons={a=guestReturns-food.headAt<35}
  assert(guestReturns-food.headAt<140,'Standing jump must genuinely hit first question')
  return
 elseif food.phase=='mushroom-collect'then
  assert(guestReturns-food.collectAt<500,'Actual mature food collection bound')
  local a=target();buttons={}
  if not a or a.state<128 then return end
  local dx=a.x-c.x;buttons={right=dx>4,left=dx< -12}
  if c.grounded and a.y<c.y-20 and not c.lastA then food.chaseJump=guestReturns end
  if food.chaseJump and guestReturns-food.chaseJump<35 then buttons.a=true end
  return
 end
