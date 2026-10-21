-- Explicit source setDir() arenas. Controller B/Select create the shots;
-- the first sixteen isolate every surface/direction at the weapon boundary.
-- The final two use real terrain/controller attachment without state forcing.
local cases={
 {name='floor-right',face=1,dir=1,dx=14,dy=19.5,aim=0},
 {name='floor-left',face=2,dir=2,dx=2,dy=19.5,aim=64},
 {name='floor-up-right',face=1,up=true,dir=3,dx=4,dy=7,aim=8},
 {name='floor-up-left',face=2,up=true,dir=3,dx=12,dy=7,aim=72},
 {name='ceiling-right',face=1,ceiling=1,dir=1,dx=14,dy=19.5,aim=0},
 {name='ceiling-left',face=2,ceiling=1,dir=2,dx=2,dy=19.5,aim=64},
 {name='ceiling-down-right',face=1,ceiling=1,down=true,dir=4,dx=4,dy=32,aim=24},
 {name='ceiling-down-left',face=2,ceiling=1,down=true,dir=4,dx=12,dy=32,aim=88},
 {name='right-wall-up',face=1,wall=1,tangent=2,dir=3,dx=1.5,dy=12,aim=72},
 {name='right-wall-down',face=1,wall=1,tangent=1,dir=4,dx=1.5,dy=24,aim=24},
 {name='right-wall-away-up',face=1,wall=1,tangent=2,left=true,dir=2,dx=-11,dy=18,aim=64},
 {name='right-wall-away-down',face=1,wall=1,tangent=1,left=true,dir=2,dx=-11,dy=18,aim=16},
 {name='left-wall-up',face=2,wall=2,tangent=2,dir=3,dx=14.5,dy=12,aim=72},
 {name='left-wall-down',face=2,wall=2,tangent=1,dir=4,dx=14.5,dy=24,aim=24},
 {name='left-wall-away-up',face=2,wall=2,tangent=2,right=true,dir=1,dx=27,dy=18,aim=80},
 {name='left-wall-away-down',face=2,wall=2,tangent=1,right=true,dir=1,dx=27,dy=18,aim=0},
 {name='controller-wall-away',face=1,wall=1,dir=2,native=true},
 {name='controller-ceiling-away',face=1,ceiling=1,dir=4,native=true},
}
local frame=0
local observed,primary,missile={},{},{}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/100),(frame-550)%100 end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',100);w('Player_Y_HighPos',1);w('Player_State',1)
 w('PlayerFacingDir',cases[n+1].face);w('PlayerStatus',1);w('InvOwnedLo',0xe3,11);w('InvSelected',1,11);w('InvAmmo',60,177)
 w('RgPreviousButtons',0);w('InvPrevious',0);w('RgCooldown',0);w('RgShootPose',0);w('RgCrouch',0);w('XgWall',0);w('XgWallContact',0);w('XgWallLock',0);w('XgCeiling',0);w('XgRise',0);w('XgJumpUsed',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 if n==16 then
  w('Player_X_Position',97);w('Player_Y_Position',150)
  for row=6,10 do for col=7,8 do w('Block_Buffer_1',0x54,row*16+col)end end
 elseif n==17 then
  w('Player_X_Position',120);w('Player_Y_Position',136)
  for col=7,10 do w('Block_Buffer_1',0x51,96+col)end
 end
 observed[n+1]=0;primary[n+1]=false;missile[n+1]=false
end
local function isolatedSurface(bank)
 local n=phase()
 if n<0 or n>=16 or r('CurrentBank')%128~=bank then return end
 local c=cases[n+1]
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',100);w('Player_Y_HighPos',1);w('Player_State',1);w('Player_Y_Speed',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('PlayerFacingDir',c.face);w('XgWall',c.wall or 0);w('XgCeiling',c.ceiling or 0);w('XgJumpUsed',c.tangent or 0)
end
emu.addMemoryCallback(function()isolatedSurface(37)end,emu.callbackType.exec,L.ExpandedWeapons)
emu.addMemoryCallback(function()isolatedSurface(6)end,emu.callbackType.exec,L.RemainingWeapons)
local pending,returns
returns={}
emu.addMemoryCallback(function()
 local n=phase()
 if n<0 or n>=#cases or r('CurrentBank')%128~=37 then return end
 local st=emu.getState();local sp=st['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 pending={n=n,sp=sp,slot=st['cpu.x']}
 if returns[pc]then return end
 returns[pc]=true
 emu.addMemoryCallback(function()
  if not pending or r('CurrentBank')%128~=37 or emu.getState()['cpu.sp']~=pending.sp+2 then return end
  local p=pending;pending=nil;local c=cases[p.n+1];local slot=p.slot
  assert(r('RgShotDir',slot)==c.dir,c.name..' source world direction actual='..r('RgShotDir',slot)..' type='..r('RgShotType',slot))
  if not c.native then
   local dx=r('RgShotX',slot)+256*r('RgShotPage',slot)+r('RgShotFracX',slot)/256-r('Player_X_Position')-256*r('Player_PageLoc')
   local dy=r('RgShotY',slot)+256*r('RgShotYHigh',slot)+r('RgShotFracY',slot)/256-r('Player_Y_Position')-256*r('Player_Y_HighPos')
   assert(dx==c.dx and dy==c.dy,c.name..' source muzzle '..dx..','..dy)
   assert(r('XgShotAim',slot)==c.aim,c.name..' source sprite rotation/mirror')
  else
   assert(c.wall and r('XgWall')~=0 or c.ceiling and r('XgCeiling')~=0,c.name..' remains attached while aiming away')
  end
  observed[p.n+1]=observed[p.n+1]+1
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaShotOrigin,'New source direction helper must exist'))
emu.addEventCallback(function()
 local n,t=phase();local c=cases[n+1]
 local b={start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0}
 if c then
  b={b=t>=20 and t<24,select=t>=40 and t<44,up=c.up,down=c.down,left=c.left,right=c.right}
  if n==16 then b.right=t<16;b.up=t<16;b.left=t>=16 end
  if n==17 then b.up=t<16;b.down=t>=16 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==#cases then print('PASS Sophia source cannon/missile vectors, muzzle positions, native wall/ceiling away controls: '..#cases..' cases');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selects Sophia');fixture(n)end
 local c=cases[n+1]
 for i=0,9 do
  local kind=r('RgShotType',i)
  if(kind==6 or kind==44 and r('SsMode',i)==1)and r('RgShotAge',i)>=2 then
   local vx=r('RgShotVXLo',i)+256*r('RgShotVXHi',i);if vx>=32768 then vx=vx-65536 end
   local vy=r('RgShotVYLo',i)+256*r('RgShotVYHi',i);if vy>=32768 then vy=vy-65536 end
   assert(c.dir==1 and vx>0 and vy==0 or c.dir==2 and vx<0 and vy==0 or c.dir==3 and vy<0 and vx==0 or c.dir==4 and vy>0 and vx==0,c.name..' accelerates along source world axis')
   if kind==6 then assert(math.max(math.abs(vx),math.abs(vy))==960,c.name..' source primary speed450/120=3.75')end
   if kind==6 then primary[n+1]=true else missile[n+1]=true end
  end
 end
 if t==85 then
  assert(observed[n+1]>=4,c.name..' actual B plus all three Select missiles exercise source origin')
  assert(primary[n+1]and missile[n+1],c.name..' primary and secondary both move correctly')
 end
end,emu.eventType.endFrame)
