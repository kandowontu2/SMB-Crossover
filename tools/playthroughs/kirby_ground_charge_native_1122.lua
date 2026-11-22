-- Continue from the first real Goomba inhale using normal pad input.
local function chargePad()
 if not charge.swallowed then return {down=true} end
 if charge.ability then return {} end
 if charge.attack then return {b=true} end
 local px, y = x(), r('Player_Y_Position')
 local ground = r('Player_State') == 0
 local float = r('KbFloat') ~= 0
 if ground and not float then
  for slot=0,5 do
   local target=actor(slot)
   local gap=target.x-px
   if charge.spawns[tostring(slot)] and target.id==6 and target.flag==1 and target.state<2
      and target.y_high==1 and math.abs(target.y-y-8)<=12 and gap>=8 and gap<=36
      and r('PlayerFacingDir')==1 and r('SavedJoypadBits')&64==0 then
    charge.attack={target=target,player=player()}
    return {b=true}
   end
  end
 end
 if px>=800 then
  charge.approach=charge.approach or player()
  return {right=px<815,left=px>827,b=float}
 end
 local b={right=true}
 for _, pipe in ipairs({{448,176},{608,160},{736,144}}) do
  local left, top=pipe[1],pipe[2]
  if left-55<=px and px<left+30 then
   if ground and not charge.pipes[tostring(left)] then
    charge.lastJump=frame;charge.pipes[tostring(left)]=true
   end
   if y>top-30 and frame-charge.lastJump>=23 then b.up=true end
   break
  end
 end
 if px>=445 and px<=480 and y>144 and not float and not ground then b.up=true end
 if float and not b.up and y<=144 and frame-charge.lastJump>24 then b.b=true end
 b.a=frame-charge.lastJump<23
 return b
end

local function chargeTick()
 if not charge.swallowed and r('KbCopy')==1 then
  assert(r('KbMouth')==0, 'Goomba was swallowed before using its copy power')
  charge.swallowed=player()
 end
 if charge.attack and not charge.hit then
  assert(frame-charge.attack.player.frame<45,'Ground charge reaches its actual target')
 end
 if not charge.hit then return end
 local result=actor(charge.hit.target.slot)
 assert(result.state&32~=0 or charge.defeated,'Body contact defeated the live target')
 charge.defeated=charge.defeated or result
 local now=r('FrameCounter')
 if charge.last~=now then
  charge.last=now
  charge.resumed=charge.resumed+1
 end
 if charge.resumed>=26 then finish('earned-ground-charge') end
end

hook('init',function(slot)
 local a=actor(slot)
 charge.spawns[tostring(slot)]=a.flag==1 and a.id==6 and a.x>352 and a.y_high==1 and a or nil
end)
hook('chargeStart',function()
 if charge.attack and not charge.ability then
  assert(r('KbCopy')==1 and r('Player_State')==0,'Grounded B starts the Goomba charge')
  charge.ability=player()
 end
end)
hook('chargeDefeat',function(slot)
 if not charge.ability or charge.hit or slot~=charge.attack.target.slot then return end
 local live=actor(slot)
 assert(live.flag==1 and live.id==6 and live.state&32==0,'Charge contacts a living Goomba')
 assert(r('KbCopy')==1 and r('KbAction')==4 and r('Player_State')==0
        and r('MmVX',1)==0 and r('MmVX',2)==3,'Actual grounded three-pixel charge velocity')
 charge.hit={target=live,player=player(),spawn=charge.spawns[tostring(slot)]}
end)
