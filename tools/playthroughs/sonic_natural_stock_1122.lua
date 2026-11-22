-- Uses the existing Sonic stage sensors and native item collector.
local items=C.item=='star' and {{kind=2,x=1616}} or {{kind=0,x=336},{kind=1,x=1248}}
local index,phase,launch=1,'route',-100
local holdA,awarded

local function steer(s,lo,hi)
 local vx=s.vx/256
 local stop=s.x+vx*math.abs(vx)/0.45
 if stop<lo then return 1 end
 if stop>hi then return 2 end
 return 0
end

local function beginJump(s,direction,hold)
 launch=s.motor
 holdA=s.motor+hold
 return direction|128
end

local function stockInput(s,item,targetX)
 local ground=s.state==0 and s.source_flags&8~=0
 local jumpReady=ground and s.motor-launch>25
 local direction=0
 if phase=='route' then
  if targetX==336 then
   if jumpReady and s.x>=200 and jumpReason(s)=='enemy' then
    phase='mushroom-hop'
    return beginJump(s,1,20)
   end
   if s.x>=282 and ground then phase='align' else direction=1 end
  elseif s.x>=targetX-56 and (C.item=='flower' or (ground and s.y==176)) then phase='align'
  else
   direction=1
   if jumpReady and jumpReason(s) then return beginJump(s,1,20) end
  end
 end
 if phase=='mushroom-hop' then
  if s.x<282 then direction=1
  elseif s.vx>0 then direction=2
  else phase='mushroom-land' end
 elseif phase=='mushroom-land' and ground and s.y==176 then
  phase='align'
 end
 if phase=='align' then
  direction=steer(s,targetX-9,targetX-6)
  if jumpReady and s.y==176 and s.x>=targetX-10 and s.x<=targetX-5 and math.abs(s.vx)<=75 then
   phase='reveal'
   return beginJump(s,0,24)
  end
  if jumpReady and s.x<targetX-12 and jumpReason(s)=='enemy' then
   return beginJump(s,direction,20)
  end
 elseif phase=='reveal' then
  if item then phase='catch'
  elseif jumpReady and s.motor-launch>60 then phase='align' end
 end
 if phase=='catch' and item then
  local dx=item.x-s.x
  direction=steer(s,item.x-7,item.x+3)
  if jumpReady and math.abs(dx)<=32 and item.y<s.y-14 then
   return beginJump(s,direction,23)
  end
 end
 return direction|((holdA and s.motor<holdA) and 128 or 0)
end

local function stockCollected(p)
 local i=items[index]
 local a=p.actor
 assert(a.kind==i.kind and births[index] and a.slot==births[index].actor.slot,
        'Native collector uses the real authored item')
 assert((sounds[32]or 0)>p.cue32 and r('FloateyNum_Control',a.slot)==6,
        'Native item disappears and queues pickup sound and points')
 if i.kind==2 then
  assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Star grants its timer and music')
 else
  assert(p.before.status==i.kind,'Naturally earned prior tier')
 end
 collections[index]={item=a,before=p.before,after=state(),boxes=p.boxes,
                      sound=r('Square2SoundQueue'),music=r('AreaMusicQueue')}
 phase='reward'
end

local function afterMain()
 if not game then return end
 updates=updates+1
 local s=state()
 local i=items[index]
 assert(identity() and s.engine~=11 and s.lives==2 and r('WorldNumber')==0 and r('LevelNumber')==0,
        'Living Sonic in the normal World 1-1 route')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats')
 headers()
 assert(updates<3300,'Bounded natural item route')
 bounded(tail,{state=s,phase=phase,pad=pad},8)
 if phase~=lastphase then
  bounded(changes,{index=index,phase=phase,state=s,pad=pad},18)
  lastphase=phase
 end
 local a
 for slot=0,5 do
  local seen=actor(slot)
  if births[index] and births[index].actor.slot==slot and seen.flag~=0 and seen.id==46 and seen.kind==i.kind then
   a=seen
  elseif not births[index] and seen.flag~=0 and seen.id==46 and seen.kind==i.kind
         and seen.state<128 and math.abs(seen.x-i.x)<=2 then
   births[index]={actor=seen,player=s}
   a=seen
  end
 end
 pad=0
 if phase=='reward' then
  local expectedStatus=i.kind<2 and i.kind+1 or collections[index].before.status
  if s.engine~=8 or r('GuestPowerupActive')~=0 then return end
  assert(s.status==expectedStatus,'Native upgrade applies before normal play resumes')
  if i.kind==2 then assert(s.star>0,'Star remains active after collection') end
  if not awarded then awarded=s end
  if motor-awarded.motor>=25 then
   collections[index].credit=awarded
   collections[index].continued=s
   if index==#items then
    assert(counts.OriginalFrame_entries==counts.OriginalFrame_returns,'Balanced original movement calls')
    finish(true,'Earned natural '..C.item..' and continued through 25 original movement calls')
    return
   end
   index=index+1
   phase='route';launch=-100;awarded=nil;holdA=nil
  end
  return
 end
 if s.engine==8 then pad=stockInput(s,a,i.x) end
end
