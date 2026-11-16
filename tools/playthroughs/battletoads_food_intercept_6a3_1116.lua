 elseif food.phase=='mushroom-collect'then
  assert(guestReturns-food.collectAt<500,'Authored mushroom ground interception bound')
  local a=target();buttons={}
  if not a or a.state<128 then return end
  buttons={right=c.x<394,left=c.x>396}
  food.intercept=food.intercept or{state=state(),actor=a,target_x=395}
  return
 end
