-- Independent pinned2.02 injury equations, explicit RAM-only native-Spiny
-- arenas. This is mechanics evidence, not a controller traversal claim.
local char=assert(HURT_CHARACTER)
local cases={}
for _,dir in ipairs({1,2})do
 for _,p in ipairs({
  {name='ground',ground=true}, {name='ascending',y=80,vy=-2},
  {name='falling',y=80,vy=3}, {name='water-ground',ground=true,water=true},
  {name='water-boundary',y=char==4 and 15 or 25,water=true},
  {name='water-boundary-fraction',y=char==4 and 15 or 25,water=true,fraction=0x8081},
  {name='fraction-page',x=dir==1 and 250 or 6,fraction=0x7f31},
  {name='saved-context',y=80,vy=-1,context=1,walk=true},
  {name='jumped-only-token',y=80,vy=-1,jumped=true},
  {name='wall-detach-token',y=80,vy=-1,wall=true},
  {name='held-jump-release',y=80,vy=-1,heldA=true,walk=true},
  {name='actual-recoil-wall',ground=true,terrain='wall'},
  {name='ceiling-jumped',y=80,vy=-2,jumped=true,terrain='ceiling'},
  {name='ceiling-not-jumped',y=80,vy=-2,terrain='ceiling'},
 })do local c={};for k,v in pairs(p)do c[k]=v end;c.dir=dir;cases[#cases+1]=c end
end
if HURT_CASE_SUBSET then
 local selected={}
 for _,c in ipairs(cases)do if HURT_CASE_SUBSET=='ceiling'and c.terrain=='ceiling'or HURT_CASE_SUBSET=='wall'and c.terrain=='wall'then selected[#selected+1]=c end end
 assert(#selected>0,'Explicit diagnostic source subset is nonempty');cases=selected
end
local frame,index,age,checks,moves,depth,uncapped,visualChecks,headQueries=0,0,0,0,0,0,0,0,0
local c,setupNext,started,ended,pending,expected,entry,immuneLast,immuneDec,worldStart,worldLive,terrainCells,ceilingSeen,wallSeen,contact
local contactReturns={}
local visual,visualReturns=nil,{}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function setq(n,v)local a=math.floor(v*65536+.5)%0x1000000;for i=0,2 do w(n,(a>>(8*i))&255,i)end end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local function y()return r('Player_Y_Position')+(r('Player_Y_HighPos')-1)*256+(r('MmYFraction')+256*r('MmYFraction',1))/65536 end
local function near(a,b,tol,n)assert(math.abs(a-b)<tol,c.name..' direction'..c.dir..' '..n..' actual'..a..' expected'..b)end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced LSR injury interrupt scope')end,emu.callbackType.exec,pc)end
local function setup()
 started=false;ended=false;pending=nil;entry=nil;expected=nil;moves=0;age=0;immuneLast=nil;immuneDec=0;worldLive=false;terrainCells={};ceilingSeen=false;wallSeen=false
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('Enemy_CollisionBits',0,i);w('RgEnemyStun',0,i);w('MmEnemyFlash',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end;for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local px=c.x or 128
 if c.terrain=='wall'then
  local col=(px+(c.dir==1 and 16 or-16))//16
  for row=0,10 do local a=208+row*16+col;w('Block_Buffer_1',0x54,a);terrainCells[a]=0x54 end
 elseif c.terrain=='ceiling'then
  local row=char==4 and 3 or 2 -- Actual world ceiling80..96 or64..80.
  for col=px//16-1,px//16+2 do local a=208+row*16+col;w('Block_Buffer_1',0xc1,a);terrainCells[a]=0xc1 end
 end
 w('Player_X_Position',px);w('Player_PageLoc',1);w('Player_Y_Position',c.ground and 176 or c.y or 80);w('Player_Y_HighPos',1)
 w('Player_State',c.ground and 0 or 2);w('PlayerStatus',1);w('PlayerSize',0);w('PlayerFacingDir',c.dir);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',3)
 w('InvOwnedLo',1,char);w('InvOwnedHi',0,char);w('InvSelected',0,char);w('InvDirty',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('PlayerChangeSizeFlag',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('GuestPowerupActive',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0)
 w('SwimmingFlag',0);w('RgAttack',0);w('RgThrust',0);w('AvSlash',0);w('AvFlip',0);w('MmFrictionYActive',0);w('MmJumpReleased',0);w('MmLastXSpeed',0);w('MmDeathFlag',0);w('MmDeathAge',0)
 w('SmBall',0);w('SmCrouch',0);w('RgCrouch',0);w('CrouchingFlag',0);w('MmSliding',0);w('MmOnVine',0);w('XgWall',0);w('XgWallLock',0);w('XgWallContact',0)
 w('PreviousA_B_Buttons',0);w('A_B_Buttons',0);w('RgPreviousButtons',0);w('SavedJoypadBits',0)
 local left=px<64 and 128 or px>240 and 384 or 256
 w('ScreenLeft_X_Pos',left%256);w('ScreenLeft_PageLoc',left//256);w('ScreenRight_X_Pos',(left+255)%256);w('ScreenRight_PageLoc',(left+255)//256);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 -- Impact admission is real ordinary Spiny contact. Source context variants
 -- below are authored only after that admission, before inventory removal.
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1)
 local impact=px+256+(c.dir==1 and-8 or 8)
 w('Enemy_X_Position',impact%256);w('Enemy_PageLoc',impact//256);w('Enemy_Y_Position',r('Player_Y_Position')+8);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
 w('Enemy_Flag',1,1);w('Enemy_ID',6,1);w('Enemy_State',0,1);w('Enemy_BoundBoxCtrl',9,1);w('Enemy_Y_HighPos',1,1);w('Enemy_PageLoc',left//256,1);w('Enemy_X_Position',(left+32)%256,1);w('Enemy_Y_Position',184,1);w('Enemy_X_Speed',8,1);w('Enemy_Y_Speed',0,1)
 worldStart=r('Enemy_X_Position',1)
end
emu.addMemoryCallback(function()
 if not c or not bank(B.GuestInjuryStart)then return end
 assert(not started,'One actual injury per arena')
 w('SwimmingFlag',c.water and 1 or 0)
 local f=c.fraction or 0;w('MmXFraction',f%256);w('MmXFraction',f//256,1)
 w('MmYFraction',f%256);w('MmYFraction',f//256,1)
 setq('MmVY',c.vy or 0);w('Player_Y_Speed',r('MmVY',2))
 w('MmFrictionYActive',char==4 and(c.context or 0)or 0);w('MmJumpReleased',0)
 w('LsrHurtFlags',c.jumped and 8 or 0);w('XgJumpUsed',c.jumped and 1 or 0)
 w('XgWall',char==10 and c.wall and 1 or 0)
 w('AvSlash',char==10 and(c.context or 0)or 0)
 w('A_B_Buttons',c.heldA and 0x80 or 0)
 w('RgPose',c.walk and 1 or 0)
 entry={x=x(),y=y(),vy=q('MmVY'),ground=r('Player_State')==0}
end,emu.callbackType.exec,assert(L.GuestInjuryStart))
local function capture(kind)
 if not c or not bank(61)then return false end
 local s=emu.getState();assert(not pending,'Non-nested owned helper API')
 pending={kind=kind,x=s['cpu.x'],y=s['cpu.y'],offset=r('ObjectOffset')};return true
end
emu.addMemoryCallback(function()
 if not capture('start')then return end
 assert(entry,'Actual Spiny injury passed common dispatch');started=true
end,emu.callbackType.exec,assert(L.LsrHurtStart))
emu.addMemoryCallback(function()
 if not c or not pending or not bank(61)then return end
 local s=emu.getState();assert(s['cpu.x']==pending.x and s['cpu.y']==pending.y and r('ObjectOffset')==pending.offset,'Injury start preserves caller X/Y/ObjectOffset independently of context')
 near(q('MmVX'),(c.dir==1 and 1 or-1)*(char==4 and 500 or 150)/120,.00002,'attacker-relative source entryVX')
 near(q('MmVY'),char==4 and entry.vy or-(char==5 and 300 or 385)/120,.00002,'source entryVY')
 assert(r('PlayerFacingDir')==(c.dir==1 and 2 or 1),'New facing is toward the actual attacker')
 assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('PlayerStatus')==0 and r('GuestHurtKind')==char,'Power loss keeps live engine and source hurt kind')
 assert(r('RgAttack')==0 and r('RgThrust')==0 and r('RgThrustReset')==0,'Damage cancels ordinary sword/whip/thrust')
 if char==4 then
  assert((r('Player_State')==0)==entry.ground,'Link preserves grounded state')
  local endpoint=(r('LsrHurtEndX')+256*r('LsrHurtEndX',1)+65536*r('LsrHurtEndX',2)+16777216*r('LsrHurtEndX',3))/65536
  near(endpoint,entry.x+(c.dir==1 and 32 or-32),.00002,'exact fractional source endpoint')
  assert((r('LsrHurtFlags')&4~=0)==(c.context==1 or c.heldA==true),'Retained/released-held-A friction context survives inventory and PHX/PHY')
  assert((r('LsrHurtFlags')&8~=0)==(c.jumped==true),'Jumped-only context never becomes friction/slash')
  -- Link source's missing"walk" label resolves to frame1 (stand), including
  -- when the pre-hit pose was a walking frame. Pixel fixture checks that art.
 elseif char==10 then
  assert(r('AvSlash')==(c.context or 0),'Pre-inventory Jump Slash survives source recoil')
  assert((r('LsrHurtFlags')&8~=0)==(c.jumped==true or c.wall==true),'Ryu jumped/wall-detach context never becomes Jump Slash')
 end
 pending=nil
end,emu.callbackType.exec,assert(L.LsrHurtStartReturned))
emu.addMemoryCallback(function()
 if not capture('move')then return end
 moves=moves+1
 assert(started and not ended,'Only locked injury integrates owned recoil')
 assert(r('A_B_Buttons')==0 and r('Left_Right_Buttons')==0 and r('Up_Down_Buttons')==0,'Source lock masks parsed actions')
 local px,py,vx,vy,ground=x(),y(),q('MmVX'),q('MmVY'),r('Player_State')==0
 local wet=c.water==true and py>(char==4 and 15 or 25)
 if ground then py=math.floor(py);vy=0;if wet and char==4 then vx=(c.dir==1 and 1 or-1)*90/120 end
 else
  if r('Player_Y_Speed')~=r('MmVY',2)then local v=r('Player_Y_Speed');vy=v>=128 and v-256 or v end
  if wet then vy=math.min(vy,250/120)end
  vy=vy+(char==4 and(wet and 500 or 1300)or char==5 and(wet and 750 or 1500)or(wet and 500 or 1400))/7200
  if char~=5 then vy=math.min(vy,(char==4 and(c.water and 500 or 800)or 700)/120)end
 end
 expected={x=px+vx,y=py+vy,vx=vx,vy=vy,wet=wet}
end,emu.callbackType.exec,assert(L.LsrHurtMovement))
emu.addMemoryCallback(function()
 if not c or not expected or not bank(61)then return end
 near(q('MmVX'),expected.vx,.00003,'source updateVX');near(q('MmVY'),expected.vy,.00004,'source gravity/pre-water/final cap order')
 if char==5 and q('MmVY')>700/120 then uncapped=uncapped+1 end
 near(x(),expected.x,.00005,'source integratedX');near(y(),expected.y,.00006,'source integratedY')
 assert((r('MmUnderwater')~=0)==expected.wet,'Hurt15/25px boundary uses strict fractional source inequality')
 assert(r('MmFrictionYActive')==0,'Link held/released jump friction is bypassed during recoil')
 checks=checks+1;expected=nil
end,emu.callbackType.exec,assert(L.LsrHurtIntegrated))
emu.addMemoryCallback(function()
 if not c or not pending or not bank(61)then return end
 local s=emu.getState();assert(s['cpu.x']==pending.x and s['cpu.y']==pending.y and r('ObjectOffset')==pending.offset,'Recoil movement preserves caller X/Y/ObjectOffset')
 pending=nil
end,emu.callbackType.exec,assert(L.LsrHurtMovementReturned))
emu.addMemoryCallback(function()
 if not c or not started or not bank(10)then return end
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 visual={sp=sp,phase=r('GuestFlickerPhase'),locked=r('GuestHurtTicks')~=0,vram=r('VRAM_Buffer1_Offset')}
 if not visualReturns[pc]then
  visualReturns[pc]=true
  emu.addMemoryCallback(function()
   if not visual or depth~=0 then return end
   if emu.getState()['cpu.sp']~=(visual.sp+2)%256 then return end
   if char==4 then
    local phase=(visual.phase+1)%6
    assert(r('GuestHurtVisible')==1 and r('GuestFlickerPhase')==phase,'Link stays opaque and its30Hz palette phase continues across recovery')
    if visual.vram<64 then
     local colors={{0x16,0x30,0x27},{0x01,0x30,0x21},{0x30,0x16,0x0c}}
     assert(r('VRAM_Buffer1',visual.vram)==0x3f and r('VRAM_Buffer1',visual.vram+1)==0x11 and r('VRAM_Buffer1',visual.vram+2)==3,'Replacement touches only the three private Link body palette colors')
     for i=1,3 do assert(r('VRAM_Buffer1',visual.vram+2+i)==colors[phase//2+1][i],'Source replacement row2/3/1 at30Hz phase'..phase)end
    end
   elseif visual.locked then assert(r('GuestHurtVisible')==1 and r('GuestFlickerPhase')==visual.phase,'Simon/Ryu recoil stays fully opaque without invented flicker')
   else
    local p=visual.phase+13
    assert(r('GuestHurtVisible')==(p>=20 and 1 or 0)and r('GuestFlickerPhase')==p%20,'Documented NES13/20 duty approximates source0.65 only after recoil')
   end
   visualChecks=visualChecks+1;visual=nil
  end,emu.callbackType.exec,pc)
 end
end,emu.callbackType.exec,assert(L.GuestLsrVisible))
emu.addMemoryCallback(function()
 if not c or not started or ended or not bank(61)then return end
 local ceiling=q('MmVY')<0 and r('Player_Y_Speed')==1
 local wall=r('Player_CollisionBits')&c.dir==0
 if ceiling then ceilingSeen=true end;if wall then wallSeen=true end
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 contact={sp=sp,x=s['cpu.x'],y=s['cpu.y'],offset=r('ObjectOffset'),wall=wall,ceiling=ceiling,vy=ceiling and(r('LsrHurtFlags')&8~=0 and 100/120 or q('MmVY'))or nil}
 if not contactReturns[pc]then
  contactReturns[pc]=true
  emu.addMemoryCallback(function()
   if not contact or depth~=0 then return end
   local s=emu.getState();if s['cpu.sp']~=(contact.sp+2)%256 then return end
   assert(s['cpu.x']==contact.x and s['cpu.y']==contact.y and r('ObjectOffset')==contact.offset,'Post-terrain helper preserves X/Y/ObjectOffset')
   if contact.ceiling then
    near(q('MmVY'),contact.vy,.00003,'Source jumped100/120 versus retainedVY at actual ceiling receipt')
    assert(r('Square1SoundQueue')&2~=0,'Actual source ceiling contact queues its common hit-ceiling cue')
   end
   if contact.wall then near(q('MmVX'),0,.00002,'Source matched-wall contact stops horizontal velocity')end
   contact=nil
  end,emu.callbackType.exec,pc)
 end
end,emu.callbackType.exec,assert(L.LsrHurtAfterCollision))
emu.addMemoryCallback(function()
 if not c or not started or not bank(10)then return end
 assert(not ended,'Exactly one source recovery');ended=true
 if c.terrain=='wall'then print('DIAG source-wall recovery c'..char..' direction'..c.dir..' moves'..moves..' X'..x()..' VX'..q('MmVX')..' bits'..r('Player_CollisionBits')..' nativeContact'..tostring(c.nativeWall))end
 if char~=4 then assert(r('Player_State')==0,'Simon/Ryu recover on actual landing, not a timer')
 else
  local endpoint=entry.x+(c.dir==1 and 32 or-32)
  if wallSeen then assert(q('MmVX')==0,'Actual into-recoil wall ends Link and stops its sourceVX')
  else near(x(),endpoint,.00002,'Link strict overshoot is clamped before recovery')end
 end
 if char==10 then assert(r('AvSlash')==0,'Ryu landing clears retained Jump Slash before enemy contact')end
end,emu.callbackType.exec,assert(L.GuestInjuryRecover))
emu.addMemoryCallback(function()
 if c and started and not ended and bank(0)and r('ObjectOffset')==1 and r('Enemy_Flag',1)~=0 then worldLive=true end
end,emu.callbackType.exec,assert(L.MoveNormalEnemy))
emu.addMemoryCallback(function()
 if char==5 and c and started and not ended and depth==0 and r('GuestHurtTicks')~=0 then
  assert(r('Player_State')~=0,'Every actual Simon hurt head query occurs while source forced-air; landing recovers before any grounded query')
  headQueries=headQueries+1
 end
end,emu.callbackType.exec,assert(L.MegaManCollisionAdder))
emu.addMemoryCallback(function()
 if not c or c.terrain~='wall'or not started or ended or depth~=0 or c.nativeWall then return end
 if r('R0')~=c.dir then return end
 c.nativeWall=true
 print('DIAG actual SamusStopAtWall c'..char..' direction'..c.dir..' X'..x()..' VX'..q('MmVX')..' PlayerCollisionBits'..r('Player_CollisionBits')..' sourceFlags'..r('LsrHurtFlags'))
end,emu.callbackType.exec,assert(L.SamusStopAtWall))
emu.addMemoryCallback(function(_,v)
 if not c or not ended then return end
 if v==75 and not immuneLast then immuneLast=75
 elseif immuneLast and v~=immuneLast then assert(v==immuneLast-1,'Source protection consumes one1250ms tick');immuneLast=v;immuneDec=immuneDec+1 end
end,emu.callbackType.write,assert(L.GuestInvulTicks))
emu.addMemoryCallback(function(_,v)
 if c and started and not ended and r('GuestHurtTicks')>0 then assert(v==0,'Locked source recoil suppresses new sword/whip/throw input')end
end,emu.callbackType.write,assert(L.RgAttack))
emu.addEventCallback(function()
 local choose=char<6 and frame>=80 and frame<80+20*char and frame%20==0 or char==10 and frame>=100 and frame<180 and frame%20==0
 local b={start=frame==60 or frame==240,right=choose,down=char==10 and frame==80}
 if c and started then b={a=true,b=true,select=true,right=true}end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 or setupNext then
  assert(r('SelectedCharacter')==char,'Actual menu launches source injury character');setupNext=false;index=index+1;c=cases[index]
  if not c then
   if char==5 and not HURT_CASE_SUBSET then
    assert(uncapped>0,'Simon source falling recoil actually exceeds Ryu700 terminal speed')
    assert(headQueries>0,'Actual Simon hurt/landing lifecycle exercises native head queries')
   end
   assert(visualChecks>#cases*74,'Source recoil/recovery visibility exercised throughout protected updates')
   print('PASS '..#cases..' source LSR injury arenas c'..char..', '..checks..' source-equation/'..visualChecks..' visibility updates: actual contact, context/ABI, live motion, lock/input, source recovery and75-update protection');emu.stop(0);return
  end
  setup();return
 end
 age=age+1
 if started then w('Enemy_Flag',0)end
 if started and not ended and r('Enemy_Flag',1)~=0 and r('Enemy_X_Position',1)~=worldStart then worldLive=true end
 if started and not ended then assert(r('GuestHurtVisible')==1,'Source Link/Simon/Ryu recoil is opaque')end
 if started and not ended then
  for a,v in pairs(terrainCells)do assert(r('Block_Buffer_1',a)==v,'Source nonInteractive preserves the authored ground/question ceiling tile')end
 end
 if ended and immuneDec==75 then
  assert(started and ended and worldLive,'Actual injury/recovery and unrelated live Goomba motion')
  assert(immuneLast==0 and immuneDec==75,'Complete separate1250ms post-recoil protection')
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'Recovery never freezes the world')
  if c.terrain=='wall'then assert(wallSeen,'Real native side contact exercised source recoil wall handling')end
  if c.terrain=='ceiling'then assert(ceilingSeen,'Real native ceiling contact exercised source jumped100 versus retainedVY')end
  setupNext=true
 end
 assert(age<400,'Bounded source injury progress')
end,emu.eventType.endFrame)
