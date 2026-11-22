-- Keep the first Goomba in Kirby's mouth while advancing to the next encounter.
local pipes={{448,176},{608,160},{736,144}}

local function spitLaneClear(px,targetX,shotY)
 local first,last=math.min(px,targetX),math.max(px,targetX)
 for _,pipe in ipairs(pipes) do
  if shotY>=pipe[2] and last>=pipe[1] and first<pipe[1]+32 then return false end
 end
 return true
end

local function spitPad()
 if spit.request then return {b=not spit.spawn} end
 local px,y=x(),r('Player_Y_Position')
 local ground=r('Player_State')==0
 if px>=590 and px<=721 and (not spit.lastSample or frame>=spit.lastSample+8) then
  spit.trace=spit.trace or {}
  if #spit.trace>=32 then table.remove(spit.trace,1) end
  spit.trace[#spit.trace+1]={p=player(),goomba=actor(0)}
  spit.lastSample=frame
 end
 if r('SavedJoypadBits')&64==0 then
  for slot=0,5 do
   local a=actor(slot)
   local gap=a.x-px
   if spit.actors[tostring(slot)] and a.flag==1 and a.id==6 and a.state<2
      and a.y_high==1 and math.abs(a.y-y-20)<=12 and math.abs(gap)>=16 and math.abs(gap)<=54
      and spitLaneClear(px+(gap>0 and 16 or 0),a.x,y+20) then
    local right=gap>0
    if r('PlayerFacingDir')~=(right and 1 or 2) then return {right=right,left=not right} end
    spit.request={target=a,player=player(),right=right}
    return {b=true}
   end
  end
 end
 local b={right=true}
 for _,pipe in ipairs(pipes) do
  local left=pipe[1]
  if px>=left-34 and px<left+15 then
   if ground and y>pipe[2]-32 and (not spit.jump or frame>=spit.jump.frame+36)
      and r('SavedJoypadBits')&128==0 then
    spit.jump=player()
    if #spit.jumps<12 then spit.jumps[#spit.jumps+1]=spit.jump end
   end
   break
  end
 end
 b.a=spit.jump and frame-spit.jump.frame<25 or false
 return b
end

local function spitTick()
 if not spit.spawn then
  assert(r('KbMouth')==7 and r('KbCopy')==0 and r('KbFloat')==0,'Mouth holds the original Goomba')
  assert(not spit.request or frame<spit.request.player.frame+12,'Native update accepts the held B press')
 elseif not spit.hit then
  assert(frame<spit.spawn.player.frame+38,'Spat star reaches the next Goomba')
 elseif spit.resumed==25 then
  finish('earned-spit-star')
 end
end

hook('init',function(slot)
 local a=actor(slot)
 spit.actors[tostring(slot)]=a.flag==1 and a.id==6 and a.x>352 and a.y_high==1 and a or nil
end)
hook('spitSpawn',function()
 if not spit.request or spit.spawn then return end
 assert(emu.getState()['cpu.a']==1 and r('KbFresh')&64~=0 and r('SavedJoypadBits')&4==0
        and r('KbMouth')==7 and r('KbCopy')==0,'Fresh B spits out the held Goomba as a star')
 spit.spawn={player=player()}
end)
hook('spitContact',function(slot)
 if not spit.spawn or spit.hit then return end
 local a=actor(slot)
 local shot=r('KbSavedSlot')
 local sx=pos('KbShotX','KbShotPage',shot)
 local sy=r('KbShotY',shot)
 assert(a.flag==1 and a.id==6 and a.state&32==0 and spit.actors[tostring(slot)],'Live authored Goomba')
 local speed=spit.request.right and 4 or 252
 assert(shot<3 and r('KbShotType',shot)==1 and r('KbShotVXHi',shot)==speed
        and r('KbShotAge',shot)>=1 and math.abs(sx-a.x)<=12 and math.abs(sy-a.y)<=12,
        'Four-pixel star overlaps the live target')
 assert(r('KbMouth')==0 and r('KbCopy')==0,'Spit consumes the held enemy without gaining a copy power')
 spit.hit={target=a,spawn=spit.actors[tostring(slot)],slot=shot,x=sx,y=sy,age=r('KbShotAge',shot)}
end)
hook('spitConsumed',function(slot)
 if not spit.hit or spit.defeated then return end
 local a=actor(slot)
 assert(slot==spit.hit.target.slot and a.state&32~=0,'Native enemy defeat returned to the star action')
 spit.defeated=a
end)
hook('spitUpdate',function()
 if not spit.defeated then return end
 assert(r('KbShotType',spit.hit.slot)==0 and r('KbMouth')==0 and r('KbCopy')==0,'Spent star remains consumed')
 spit.resumed=spit.resumed+1
end)
