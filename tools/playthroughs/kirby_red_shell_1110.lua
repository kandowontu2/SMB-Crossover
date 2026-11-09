-- Controller-only flight to the first native 4-3 mushroom and its Red Koopas.
local function steer(facing, b)
 return {right=facing==1,left=facing==2,b=not not b}
end
local function partner(origin)
 local nearest
 for slot in pairs(births) do
  local a=actor(slot)
  if (not capture or slot~=capture.target.slot) and a.id==3 and a.flag==1 and a.state<2 and aligned(a) and
     (not nearest or math.abs(a.x-origin)<math.abs(nearest.x-origin)) then nearest=a end
 end
 return nearest
end
local function naturalControls()
 local wx,wy=x(),r('Player_Y_Position')+256*(r('Player_Y_HighPos')-1)
 local grounded=r('Player_State')==0 and r('KbFloat')==0
 local face=r('PlayerFacingDir')
 if hit then return {} end
 if erased and r('KbMouth')~=0 then return {down=true} end
 if capture and not erased then return {} end
 if inhaleInput and not erased then return steer(inhaleInput.facing,true) end
 if shotInput then return steer(shotInput.facing,frame-shotInput.player.frame<=18) end
 local target=partner(wx)
 if grounded and (wx>=391 or erased) and target and r('KbHurt')==0 and r('InjuryTimer')==0 then
  local gap=math.abs(target.x-wx)
  local direction=target.x>=wx and 1 or 2
  if not erased and r('KbCopy')==0 and r('KbMouth')==0 and gap<=56 then
   if face~=direction then return steer(direction,false) end
   approachHP=r('KbHealth')
   inhaleInput={player=player(),target=target,gap=gap,facing=direction}
   return steer(direction,true)
  end
  if erased and r('KbCopy')==3 and gap<=42 then
   if face~=direction then return steer(direction,false) end
   shotInput={player=player(),target=target,gap=gap,facing=direction}
   return steer(direction,true)
  end
  if not erased or r('KbCopy')==3 then return steer(direction,false) end
 end
 -- Fly above the Y80 mushroom ending at X384, then descend onto the
 -- lower Y144 ledge while staying left of the two authored Koopas.
 if wx<391 then
  local rise=wx<335 or wy>77 or r('KbFloat')==0
  return {right=true,a=rise,up=rise and not grounded}
 end
 if not grounded and wx<405 and wy<104 then return {right=true} end
 if grounded and wx<425 then return {right=true} end
 return {}
end
