-- Keep the successful first 4-3 landing and capture. If its partner leaves,
-- fly over the high mushrooms and land by the third authored Red Koopa.
local phase='first-ledge'
local function steer(facing, b)
 return {right=facing==1,left=facing==2,b=not not b}
end
local function mark(name)
 local slots={}
 for i=0,5 do slots[#slots+1]=actor(i) end
 routeEvents[#routeEvents+1]={event=name,player=player(),slots=slots}
end
local function change(nextPhase)
 phase=nextPhase
 mark(nextPhase)
end
local function partner(origin, wanted)
 local nearest
 for slot,born in pairs(births) do
  local a=actor(slot)
  local allowed=(not capture or born~=capture.birth) and ((wanted==624)==(born.x==624))
  if allowed and a.id==3 and a.flag==1 and a.state<2 and aligned(a) and
     (not nearest or math.abs(a.x-origin)<math.abs(nearest.x-origin)) then nearest=a end
 end
 return nearest
end
local function aim(target, wx, face, range)
 if not target then return end
 local gap=math.abs(target.x-wx)
 if gap>range then return end
 local facing=target.x>=wx and 1 or 2
 if face~=facing then return steer(facing,false) end
 shotInput={player=player(),target=target,birth=births[target.slot],gap=gap,facing=facing}
 mark('shot-decision')
 return steer(facing,true)
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
 if erased and r('KbCopy')==3 then
  if phase=='first-ledge' then
   local target=partner(wx,448)
   local input=grounded and aim(target,wx,face,42)
   if input then return input end
   change('raise-from-first-ledge')
  end
  if phase=='raise-from-first-ledge' then
   if wy>21 then return {a=true,up=not grounded} end
   change('cross-high-mushroom')
  end
  if phase=='cross-high-mushroom' then
   if wx<591 then return {right=true,a=true,up=not grounded} end
   change('release-over-lower-ledge')
  end
  if phase=='release-over-lower-ledge' then
   if not grounded or wy<150 then return {} end
   change('lower-ledge-landing')
  end
  local target=partner(wx,624)
  local input=grounded and aim(target,wx,face,42)
  if input then return input end
  if grounded and target then
   local direction=target.x>=wx and 1 or 2
   if wx>=583 and wx<653 then return steer(direction,false) end
  end
  return {}
 end
 local target=partner(wx,448)
 if grounded and wx>=391 and target and r('KbHurt')==0 and r('InjuryTimer')==0 then
  local gap=math.abs(target.x-wx)
  local direction=target.x>=wx and 1 or 2
  if r('KbCopy')==0 and r('KbMouth')==0 and gap<=56 then
   if face~=direction then return steer(direction,false) end
   approachHP=r('KbHealth')
   inhaleInput={player=player(),target=target,gap=gap,facing=direction}
   return steer(direction,true)
  end
  return steer(direction,false)
 end
 if wx<391 then
  local rise=wx<335 or wy>77 or r('KbFloat')==0
  return {right=true,a=rise,up=rise and not grounded}
 end
 if not grounded and wx<405 and wy<104 then return {right=true} end
 if grounded and wx<425 then return {right=true} end
 return {}
end
