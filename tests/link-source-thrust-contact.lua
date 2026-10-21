-- Explicit directional-contact arenas, never stage-clear evidence. Oracle is
-- pinned2.02 HitTester.checkLastHitPoints/calcAxis and Link.hitEnemy.
local frame,depth,index,pending,needArena=0,0,1,nil,true
local cases={}
local shapes={
 {name='from-above',lastP={124,124,140,155},p={124,136,140,167}},
 {name='upper-left-corner',lastP={108,124,124,155},p={120,136,136,167}},
 {name='upper-right-corner',lastP={140,124,156,155},p={128,136,144,167}},
 {name='from-below',lastP={124,176,140,207},p={124,170,140,201}},
 {name='lower-left-vertical',lastP={108,176,124,207},p={120,170,136,201}},
 {name='lower-left-horizontal',lastP={108,176,124,207},p={110,160,126,191}},
 {name='lower-right-vertical-tie',lastP={140,176,156,207},p={135,170,151,201}},
 {name='side-foot-padding7',lastP={108,136,124,167},p={110,136,126,167}},
 {name='side-foot-padding8',lastP={108,137,124,168},p={110,137,126,168}},
 {name='grounded-side',lastP={108,136,124,167},p={110,136,126,167},ground=true},
 {name='existing-overlap',lastP={124,148,140,179},p={124,148,140,179}},
}
local enemy={124,160,140,175}
local function side(c)
 local lp,p,e=c.lastP,c.p,enemy
 if lp[4]<=e[2]then return 1 end
 if lp[2]>=e[4]then
  local dx=nil
  if lp[3]<=e[1]then dx=p[3]-e[1]elseif lp[1]>=e[3]then dx=e[3]-p[1]end
  if not dx or e[4]-p[2]<=dx then return 2 end
  return 0
 end
 if lp[3]<=e[1]or lp[1]>=e[3]then
  local pen=p[4]-e[2]
  if not c.ground and pen>=0 and pen<=15/2 then return 1 end
 end
 return 0
end
for power=0,2 do for direction=0,2 do for _,shape in ipairs(shapes)do
 local c={power=power,direction=direction}
 for k,v in pairs(shape)do c[k]=v end
 cases[#cases+1]=c
end end end
for _,extra in ipairs({'receipt','previous-overlap','immune','invalid-cache','reused-slot'})do
 cases[#cases+1]={name=extra,power=1,direction=1,lastP=shapes[1].lastP,p=shapes[1].p,
  receipt=extra=='receipt',previous=extra=='previous-overlap',immune=extra=='immune',
  invalid=extra=='invalid-cache',reused=extra=='reused-slot'}
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function raw(n)local q=r(n)+256*r(n,1)+65536*r(n,2);return q>=0x800000 and q-0x1000000 or q end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link thrust interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()emu.setInput({right=frame>=80 and frame<160 and(frame-80)%20==0,start=frame==200},0)end,emu.eventType.inputPolled)
local function arena()
 w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestFlickerPhase',0);w('GuestHurtVisible',1);w('LsrHurtFlags',0)

 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',146);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('GameEngineSubroutine',8);w('AreaType',1);w('SwimmingFlag',0);w('TimerControl',0);w('GuestPowerupActive',0)
 w('Player_State',2);w('PlayerStatus',1);w('PlayerSize',0);w('Player_X_Speed',0);w('Player_Y_Speed',2)
 w('StarInvincibleTimer',0);w('InjuryTimer',0);w('StompTimer',0);w('Enemy_CollisionBits',0)
 w('RgAttack',0);w('RgThrust',0);w('RgThrustReset',0);w('RgCrouch',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end;w('MmVY',2,2)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
end
emu.addMemoryCallback(function()
 if frame<560 or depth~=0 or r('CurrentBank')%128~=8 then return end
 -- LinkBodyContact is emitted in GUEST (bank8); ROSTER movement is bank22.
 assert(not pending,'Each contact completes before the next helper entry')
 local c=cases[index];assert(c,'Bounded source contact cases')
 local s=emu.getState();pending={c=c,x=s['cpu.x'],y=s['cpu.y']}
 for i=0,3 do w('LinkLastBoxes',c.lastP[i+1],i);w('LinkLastBoxes',enemy[i+1],4+i);w('BoundingBox_UL_Corner',c.p[i+1],i);w('BoundingBox_UL_Corner',enemy[i+1],4+i)end
 local id=c.immune and 2 or 6
 w('Enemy_ID',id);w('LinkLastIds',c.reused and id+1 or id);w('LinkLastValid',c.invalid and 0 or 1)
 w('RgThrust',c.direction);w('Player_State',c.ground and 0 or 1);w('PlayerStatus',c.power);w('InvOwnedLo',0,4);w('InvOwnedHi',0,4)
 w('LinkThrustReceipt',c.receipt and 1 or 0);w('LinkThrustPrev',c.previous and 1 or 0);w('LinkThrustNow',0)
 local hp=500-(c.receipt and 75 or 0);w('MmEnemyHealthLo',hp%256);w('MmEnemyHealthHi',math.floor(hp/256))
 w('MmVY',0);w('MmVY',0,1);w('MmVY',c.direction==2 and 254 or 2,2)
end,emu.callbackType.exec,assert(L.LinkBodyContact))
local function result(protected)
 if not pending or depth~=0 or r('CurrentBank')%128~=8 then return end
 local c=pending.c;local expected=c.direction~=0 and side(c)==c.direction and not c.invalid and not c.reused
 assert(protected==expected,'Link2.02 matching body side '..c.name..' power'..c.power..' direction'..c.direction)
 local s=emu.getState();assert(s['cpu.x']==pending.x and s['cpu.y']==pending.y,'Link body carry API preserves caller X/Y')
 local hp=500-(c.receipt and 75 or 0)
 if expected and not c.receipt and not c.immune then hp=hp-({50,75,100})[c.power+1]end
 assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==hp,'Exactly the shared source-damage receipt for '..c.name)
 if expected and not c.receipt then
  local vy=raw('MmVY')/65536
  assert(math.abs(vy-(c.direction==1 and -325/120 or 0))<.00002,'Down bounce325 / Up cancel, including immune contact '..c.name)
  assert(r('LinkThrustReceipt')==1,'Matching body and virtual contact share one receipt')
 end
 pending=nil;index=index+1;needArena=true
 if not cases[index]then print('PASS '..#cases..' Link source directional body contacts, immunity, ring damage, shared receipt and repeat-contact recovery');emu.stop(0)end
end
emu.addMemoryCallback(function()result(true)end,emu.callbackType.exec,assert(L.LinkBodyContactProtected))
emu.addMemoryCallback(function()result(false)end,emu.callbackType.exec,assert(L.LinkBodyContactOrdinary))
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==4,'Real menu launches Link before source contact arenas')end
 if frame>=560 and not pending and needArena then arena();needArena=false end
 assert(frame<1600,'Every source body-contact case reaches the real helper')
end,emu.eventType.endFrame)
