  -- Settle early in the clear ground lane. The Koopa walks toward Kirby
  -- while the unchanged route's repeated jumps can cross over it.
  if koopa then
   local a=actor(koopa.slot)
   local gap=a.x-wx
   if aligned(a) and a.id==0 and a.state==0 and r('PlayerFacingDir')==1 and
      r('Player_State')==0 and r('KbFloat')==0 and r('KbHurt')==0 and r('InjuryTimer')==0 and
      r('KbAction')==0 and gap>=20 and gap<=56 then
    approachHP=r('KbHealth')
    inhaleInput={player=player(),target=a,gap=gap}
    return {right=true,b=true}
   end
   if a.flag==1 and a.id==0 and gap>=0 and gap<=74 then return {} end
  end
  if wx<1540 or (wx<1600 and r('Player_State')==0 and r('Player_Y_Position')<176) then
   return {right=true}
  end
  return {}
