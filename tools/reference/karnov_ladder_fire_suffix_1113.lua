-- Ordinary controls after the genuinely used Bomb; no game-state writes.
local normalFire={phase='await-retired-bomb',contacts={},rejections={},aims={}}
stockFifth.normal_fire=normalFire
local function fireReject(reason,a,x,y,block)
 normalFire.rejections[reason]=(normalFire.rejections[reason]or 0)+1
 normalFire.last_rejected={reason=reason,actor=a,s=state(),block=block}
end
local function openLowShot(x,y,a)
 if a.x<=x+20 then return false,'behind-or-too-close'end
 if a.x-x>=100 then return false,'range'end
 -- Preserve the owning KrCombatBlock predicate: shots may activate native
 -- bumpable tiles and break51 / non-terrain52. Hard solids still block aim.
 for xx=((x+16)//8)*8,a.x,8 do
  for yy=y+8,y+24,8 do
   local t=tile(xx,yy)
   if emu.read(MTILE_ATTRIBUTES_OFFSET+t,emu.memType.nesPrgRom)&1~=0 then
    local cell=((xx//256)%2)*208+((yy-32)//16)*16+(xx%256)//16
    local terrain=emu.read(FIRE_TERRAIN_BASE+cell,emu.memType.nesDebug)
    local attackable=t==81 or(t==82 and terrain==0)or t==192 or t==193 or(t>=85 and t<=94)
    if not attackable then return false,'masonry',{tile=t,terrain=terrain,x=xx,y=yy}end
    normalFire.breakable_corridor=normalFire.breakable_corridor or{tile=t,terrain=terrain,x=xx,y=yy,s=state()}
   end
  end
 end
 return true
end
local function frontGoomba(x,y,d)
 for i=0,5 do local a=actor(i)
  if a.flag>0 and a.flag<128 and a.id==6 and a.state&32==0 and math.abs(a.y-y)<24 and math.abs(a.x-x)<d then
   local ok,why,block=openLowShot(x,y,a)
   if ok then return a end
   fireReject(why,a,x,y,block)
  end
 end
end
local originalFifthClear=fifthClearEnemy
fifthClearEnemy=function(x,y)
 if #pickups~=4 then return originalFifthClear(x,y)end
 local a=frontGoomba(x,y,100);if not a then return nil end
 if not normalFire.last_aim or normalFire.last_aim.slot~=a.slot then
  normalFire.last_aim={slot=a.slot,actor=a,s=state()}
  normalFire.aims[#normalFire.aims+1]=normalFire.last_aim
  if #normalFire.aims>12 then table.remove(normalFire.aims,1)end
 end
 -- Source crouch fire is the original low shot; standing fire passes over
 -- low Goombas. Face once, then hold distance instead of chasing the actor.
 if r('PlayerFacingDir')~=1 then return 1 end
 normalFire.source_clock=kr(0xe8)
 return 4+(normalFire.source_clock%12<6 and 64 or 0)
end
local originalFifthNear=fifthEnemyNear
fifthEnemyNear=function(x,d)
 if #pickups~=4 then return originalFifthNear(x,d)end
 return frontGoomba(x,r('Player_Y_Position'),d)~=nil
end
local originalFireControl=control
control=function(...)
 if #pickups==4 and armed and blastSeen and kr(0xc0)==0 then
  if not normalFire.retired then normalFire.retired=state();normalFire.since=frame end
  if kr(0x8e)~=255 then
   normalFire.phase='select-normal-fire'
   assert(frame-normalFire.since<80,'Ordinary Select reaches normal FIRE after consumed Bomb')
   return(frame-normalFire.since)%8<2 and 32 or 0
  end
  if not normalFire.ready then normalFire.ready=state()end
  normalFire.phase='normal-fire'
 end
 local pad=originalFireControl(...)
 normalFire.requested_pad=pad
 return pad
end
emu.addMemoryCallback(function()
 if done or not game or #pickups~=4 or not normalFire.ready or kr(0xc0)~=0 then return end
 local at=emu.convertAddress(L.HandleEnemyFBallCol)
 if not at or at.memType~=emu.memType.nesPrgRom or at.address~=FIRE_CONTACT_OFFSET then return end
 local c=emu.getState();local slot=c['cpu.x'];if slot>5 then return end
 normalFire.contact_count=(normalFire.contact_count or 0)+1
 if #normalFire.contacts>=12 then return end
 local sp=c['cpu.sp'];local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local q={before=actor(slot),s=state(),return_pc=pc,return_sp=(sp+2)&255}
 normalFire.contacts[#normalFire.contacts+1]=q
 emu.addMemoryCallback(function()
  if done or q.after then return end
  local c=emu.getState();if c['cpu.sp']~=q.return_sp then return end
  q.after=actor(slot);q.popup=r('FloateyNum_Control',slot)
  q.retired=q.after.flag==0 or q.after.state&32~=0
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,L.HandleEnemyFBallCol)
