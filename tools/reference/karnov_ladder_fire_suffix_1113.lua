-- Ordinary controls after the genuinely used Bomb; no game-state writes.
local normalFire={phase='await-retired-bomb',contacts={},rejections={},aims={}}
stockFifth.normal_fire=normalFire
local function fireReject(reason,a,x,y,block)
 normalFire.rejections[reason]=(normalFire.rejections[reason]or 0)+1
 normalFire.last_rejected={reason=reason,actor=a,s=state(),block=block}
end
local function shotCell(xx,yy)
 local t=tile(xx,yy)
 local cell=((xx//256)%2)*208+((yy-32)//16)*16+(xx%256)//16
 local terrain=emu.read(FIRE_TERRAIN_BASE+cell,emu.memType.nesDebug)
 local pass=t==0 or t==35 or t==38 or t==194 or t==195 or t==95 or t==96
 local brick=t==81 or(t==82 and terrain==0)
 local attackable=brick or t==192 or t==193 or(t>=85 and t<=94)
 return{tile=t,terrain=terrain,x=xx,y=yy,brick=brick,pass=pass,
  blocked=not(pass or attackable)and emu.read(MTILE_ATTRIBUTES_OFFSET+t,emu.memType.nesPrgRom)&1~=0,
  attackable=attackable}
end
local function openLowShot(x,y,a)
 if a.x<=x+20 then return false,'behind-or-too-close'end
 if a.x-x>=100 then return false,'range'end
 -- Original crouch state6 uses FAFD[6]=$18 against sourceY=nativeY+32.
 -- The native combat center is that shot anchor+8+4: nativeY+20.
 for xx=((x+16)//8)*8,a.x,8 do
  local q=shotCell(xx,y+20)
  if q.blocked then return false,'masonry',q end
  if q.attackable then normalFire.breakable_corridor=normalFire.breakable_corridor or{cell=q,s=state()}end
 end
 return true
end
local function terrainFire(x,y)
 -- Standing state0 uses FAFD[0]=$20: combat center nativeY+12.
 -- Clear each actual body-height brick row with the appropriate original
 -- shot before walking; do not rely on an enemy to trigger brick firing.
 local xx=((x+16)//16)*16
 for _,aim in ipairs({{center=12,down=false},{center=20,down=true}})do
  local q=shotCell(xx,y+aim.center)
  local prior=normalFire.terrain_aim
  if q.brick or(q.tile==35 and prior and prior.cell.x==xx and prior.down==aim.down)then
   normalFire.terrain_aim={cell=q,down=aim.down,s=state()}
   normalFire.terrain_calls=(normalFire.terrain_calls or 0)+1
   if r('PlayerFacingDir')~=1 then return 1 end
   return(aim.down and 4 or 0)+(kr(0xe8)%12<6 and 64 or 0)
  end
 end
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
  if r('Player_State')==0 and(stockFifth.stage=='travel'or stockFifth.stage=='bump')then
   local pad=terrainFire(wx(),r('Player_Y_Position'));if pad~=nil then normalFire.requested_pad=pad;return pad end
  end
 end
 local pad=originalFireControl(...)
 normalFire.requested_pad=pad
 return pad
end
local checkedFireControl=control
control=function(...)
 local ok,pad=pcall(checkedFireControl,...)
 if not ok then finish(false,'normal-fire: '..tostring(pad));return 0 end
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
