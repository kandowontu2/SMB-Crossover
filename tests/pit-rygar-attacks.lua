-- Controller attacks after explicit empty, flat terrain fixtures. This is
-- posture/weapon regression evidence, not a controller-only level clear.
local frame=0
local c=assert(EXPANDED_CHARACTER)
local previous,peak,returned,rendered
local samples={}
local checked=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function active()
 for i=0,9 do if r('RgShotType',i)>0 then return i end end
end
local function snapshot(tag)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-attack-'..c..'-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function fixture(power,dir)
 w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',dir);w('PlayerStatus',power)
 w('RgAttack',0);w('RgCooldown',0);w('RgShootPose',0);w('XgDiskReach',0);w('XgDiskReturning',0)
 for i=0,9 do w('RgShotType',0,i) end
 for i=0,2 do w('MmVY',0,i);w('MmVX',0,i) end
 previous=nil;peak=0;returned=false;rendered=false
end
local function case()
 if frame<550 then return nil end
 local n=math.floor((frame-550)/100)
 return n,(frame-550)%100
end
emu.addEventCallback(function()
 local n,t=case()
 emu.setInput({down=frame==80 or (n and n<6 and t>=5 and t<85),
  right=frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0,start=frame==200,
  b=n and ((n<6 and t==12) or (n==6 and t==17) or (n==7 and t==17)),
  a=n and n>=6 and t>=10 and t<30,up=n==7,
  select=c==6 and n==8 and t==17},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 local n,t=case()
 if not n then return end
 if frame==550 then
  assert(r('SelectedCharacter')==c,'Expected character selected')
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
 end
 if t==0 and n<9 then fixture(n<6 and math.floor(n/2) or 0,n%2==0 and 1 or 2) end
 if n<6 then
  if t==10 then assert(r('RgCrouch')~=0,'Down crouches before attacking') end
  if t==15 then
   checked=checked+1
   assert(r('RgCrouch')~=0 and r('CrouchingFlag')~=0,'Attacking keeps crouching collision')
   assert(r('RgPose')==L.XG_POSE_CROUCHSHOOT,'Crouching attack keeps the short body frame, case '..n..' pose '..r('RgPose')..' shoot '..r('RgShootPose')..' reach '..r('XgDiskReach'))
   assert(r('RgAttack')==0,'Down+B fires the primary weapon')
   local i=assert(active(),'Crouched primary weapon is active')
   assert(r('RgShotY',i)==r('Player_Y_Position')+(c==7 and 15 or 25),'Weapon leaves the lowered hand')
   snapshot('crouch-'..n)
  end
  if c==7 and t>=13 and t<85 then
   local i=active()
   if i and r('RgShotAge',i)>=3 then
    local x=r('RgShotX',i)+256*r('RgShotPage',i)
    local hand=r('Player_X_Position')+256*r('Player_PageLoc')+8
    local distance=math.abs(x-hand)
    local reach=({40,64,88})[math.floor(n/2)+1]-(n%2==1 and 2 or 0)
    assert(distance<=reach,'Diskarmor stays within upgraded reach')
    if previous then
     assert(math.abs(distance-previous)==4,'Diskarmor extends/retracts four pixels per frame without jitter: '..distance..'/'..previous)
     if distance<previous then returned=true end
     if returned then assert(distance<previous,'Returning Diskarmor never reverses away from the hand') end
    end
    peak=math.max(peak,distance);previous=distance
    local links=0
    local chainTile=emu.read(0x20*0x2000+(L.XgRYGARWeapon8Right+1)%0x2000,emu.memType.nesPrgRom)
    for o=0,255,4 do
     if r('Sprite_Y_Position',o)<240 and r('Sprite_Tilenumber',o)==chainTile then links=links+1 end
    end
    if distance>=24 then assert(links>=1,'Chain graphics reach OAM throughout extension and return');rendered=true end
    assert(links==1,'Original Rygar has one short chain tail sprite')
    for line=176,207 do
     local count=0
     for o=0,255,4 do local y=r('Sprite_Y_Position',o)+1;if y<=line and line<y+16 then count=count+1 end end
     assert(count<=8,'Rygar, Diskarmor and chain fit eight sprites per scanline when alone: '..count)
    end
    samples[#samples+1]=table.concat({n,t,distance,links},',')
    if n==4 and t>=14 and t<=60 then snapshot('chain-'..t) end
   end
  end
  if t==85 and c==7 then
   assert(active()==nil and returned and rendered,'Diskarmor completes its return and chain animation case '..n)
   assert(peak==({40,64,88})[math.floor(n/2)+1]-(n%2==1 and 2 or 0),'All three Diskarmor reaches are exercised')
  end
 elseif n==6 or n==7 then
  if t==21 then
   assert(r('Player_State')~=0,'Attack occurs during a real jump')
   assert(active()~=nil,'Airborne primary weapon fires')
   assert(r('RgPose')==(c==6 and n==7 and L.XG_POSE_JUMPUP or L.XG_POSE_JUMPSHOOT),'Airborne attack preserves airborne legs')
   snapshot('air-'..n)
  end
 elseif n==8 and c==6 and t==23 then
  assert(r('RgAttack')>0 and r('RgPose')>=L.XG_POSE_JUMPATTACK1,'Select swings the hammer with airborne legs')
  snapshot('air-hammer')
 end
 if frame==1450 then
  assert(checked==6,'All six ducking attack cases actually completed: '..checked)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-attack-'..c..'-trace.csv','w'));f:write('case,frame,distance,chain_sprites\n'..table.concat(samples,'\n'));f:close()
  assert(r('GameEngineSubroutine')==8,'Attacks preserve active gameplay')
  print('PASS '..(c==6 and 'Pit crouch arrows, ground/air bow poses, upward air shot and Select hammer' or 'Rygar crouch/air attacks and smooth complete Diskarmor/chain return, both directions and all upgrades'))
  emu.stop(0)
 end
end,emu.eventType.endFrame)
