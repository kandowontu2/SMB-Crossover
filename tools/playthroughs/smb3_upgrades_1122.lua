-- Separate natural Mushroom/suit route. The pinned first-M controller is
-- injected unchanged; progress below is observer-owned Lua state, never RAM.
local base=assert(SMB3_UPGRADE_BASE)
local progress=assert(SMB3_UPGRADE_PROGRESS)
local mode=assert(SMB3_UPGRADE_MODE)
assert(mode=='mushroom' or mode=='mushroom-suit')
local phase,at,lastJump,hold='mushroom',0,-100,-1
local defense,defenseAt=false,0
local geometry=nil
local T={phase=phase,changes={},defense_jumps={}}
SMB3_UPGRADE_STATE=T
local function change(c,p)
 phase=p;at=c.update;T.phase=p
 T.changes[#T.changes+1]={phase=p,update=c.update,x=c.x,y=c.y,vx=c.vx}
 if #T.changes>24 then table.remove(T.changes,1)end
end
local function steer(c,goal,tolerance)
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local dx=goal-c.x;local lead=vx*vx/24+6;local band=tolerance or 3
 if vx>3 and dx<=lead then return {left=true}end
 if vx< -3 and -dx<=lead then return {right=true}end
 if dx>band then return {right=true}end
 if dx< -band then return {left=true}end
 if vx>0 then return {left=true}end
 if vx<0 then return {right=true}end
 return {}
end
local function defend(c)
 if defense then
  if c.grounded and c.update-defenseAt>4 then defense=false
  else return {right=true,a=c.update<hold}end
 end
 local e=c.enemy()
 if c.grounded and not c.lastA and c.update-lastJump>24 and e and e.dx>12 and e.dx<=64
    and e.y>=c.y-24 and e.y<=c.y+88 then
  defense=true;defenseAt=c.update;lastJump=c.update;hold=c.update+18
  T.defense_jumps[#T.defense_jumps+1]={update=c.update,x=c.x,y=c.y,enemy=e}
  assert(#T.defense_jumps<=8,'Bounded genuine defensive jumps')
  return {right=true,a=true}
 end
end
local function suitActor(c)
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i);local stamp=c.r('InvPickup',i)
  if flag>0 and flag<128 and c.r('Enemy_ID',i)==46 and c.r('InvPickupOwner',i)==17
     and stamp>=0xd2 and stamp<=0xd6 then
   return {slot=i,stamp=stamp,state=c.r('Enemy_State',i),
    x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
  end
 end
end
local function solid(c,x,y)
 local t=c.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
return function(c)
 local ordinary=base(c)
 if c.char~=17 or c.world~=0 or c.level~=0 then return ordinary end
 if c.r('M3Growth')~=0 or c.r('M3Poof')~=0 then return {}end
 if not progress.mushroom then
  if c.r('M3Form')==0 then return ordinary end
  return defend(c)or{}
 end
 if mode=='mushroom' or progress.suit then return defend(c)or{}end
 if progress.suit_collected then return defend(c)or{}end
 assert(c.r('M3Form')>=1,'Earned Super form lost before the authored suit block; Mushroom checkpoint remains valid')
 if phase=='mushroom'then change(c,'travel')end
 if phase=='travel'then
  if c.x<1152 then return defend(c)or ordinary end
  defense=false;change(c,'suit-brake')
 end
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local a=suitActor(c)
 if a and not geometry then
  local row
  for _,y in ipairs({144,128})do if solid(c,1256,y)then row=y;break end end
  -- The item appears before the bouncing block returns to the collision map.
  if not row then
   assert(c.update-lastJump<=55,'Bounced upgrade block did not settle')
   return steer(c,1244,2)
  end
  local left=1248
  for _=1,12 do if not solid(c,left-8,row)then break end;left=left-16 end
  geometry={row=row,left=left,stage=left-40,actor=a};T.geometry=geometry
  change(c,'suit-stage')
 end
 if geometry and a then
  if phase=='suit-stage'then
   if c.grounded and c.y>=160 and math.abs(c.x-geometry.stage)<=3 and math.abs(vx)<=3
      and a.state&128~=0 and not c.lastA then
    lastJump=c.update;hold=c.update+24;change(c,'suit-jump');return {right=true,a=true}
   end
   return steer(c,geometry.stage)
  elseif phase=='suit-jump'then
   if c.grounded and c.update-at>4 then
    if c.y+32<=geometry.row+2 then change(c,'suit-walk')
    else
     T.row_retries=(T.row_retries or 0)+1;assert(T.row_retries<=4,'Bounded actual suit-row crossing attempts')
     change(c,'suit-stage')
    end
   end
   local b=steer(c,a.x-4,2);b.a=c.update<hold;return b
  elseif phase=='suit-walk'then return steer(c,a.x-4,2)end
 end
 if phase=='suit-brake'then
  if vx>2 then return {left=true}end
  if vx< -2 then return {right=true}end
  change(c,'suit-position')
 end
 if phase=='suit-position'then
  if not(c.grounded and c.y>=160)then return steer(c,1208)end
  if math.abs(c.x-1244)<=2 and math.abs(vx)<=3 and not c.lastA and c.update-lastJump>24 then
   T.head_attempts=(T.head_attempts or 0)+1;assert(T.head_attempts<=8,'Bounded authored suit head attempts')
   lastJump=c.update;hold=c.update+18;change(c,'suit-bump');return {a=true}
  end
  return steer(c,1244,2)
 elseif phase=='suit-bump'then
  if c.update-at>75 and c.grounded then change(c,'suit-position')end
  local b=steer(c,1244,2);b.a=c.update<hold;return b
 end
 return {}
end
