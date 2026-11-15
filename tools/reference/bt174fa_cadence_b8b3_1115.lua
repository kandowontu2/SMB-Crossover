local C={["cycle"]=0,["hooks"]={["FlagpoleRoutine"]={["bank"]=126,["bank_SHA256"]="5bd9cd2fce2eaa0b6bd14b403a3ea0fb4c979499087d3df5c2c330bdffa5a331",["bytes"]={162,5,181,23,201,48,240,5},["offset"]=1033809,["pc"]=34385},["GameLoop"]={["bank"]=126,["bank_SHA256"]="5bd9cd2fce2eaa0b6bd14b403a3ea0fb4c979499087d3df5c2c330bdffa5a331",["bytes"]={169,255,141,57,1,32,86,131},["offset"]=1032921,["pc"]=33497},["GameLoopReturn0"]={["bytes"]={104,205,58,1,240,238,32,196},["offset"]=1032894,["pc"]=33470},["GameLoopReturn1"]={["bytes"]={104,169,0,141,59,1,76,178},["offset"]=1032912,["pc"]=33488},["PlayerBGCollision"]={["bank"]=126,["bank_SHA256"]="5bd9cd2fce2eaa0b6bd14b403a3ea0fb4c979499087d3df5c2c330bdffa5a331",["bytes"]={173,25,7,208,46,165,15,201},["offset"]=1039195,["pc"]=39771},["PlayerMovementSubs"]={["bank"]=1,["bank_SHA256"]="96a320b5a2e429e253e9c8a659ce877650305648f4037cc1db0533517b0c58a0",["bytes"]={173,2,96,208,18,141,106,1},["offset"]=9687,["pc"]=42455},["PlayerPhysicsSub"]={["bank"]=1,["bank_SHA256"]="96a320b5a2e429e253e9c8a659ce877650305648f4037cc1db0533517b0c58a0",["bytes"]={165,30,201,3,208,36,160,0},["offset"]=10228,["pc"]=42996},["PositionPlayerOnHPlat"]={["bank"]=0,["bank_SHA256"]="364bbbe15b880b684415b6329b65c7121f79750ae473f5d635aea5982fd3ca37",["bytes"]={165,117,24,101,3,133,117,165},["offset"]=5763,["pc"]=46723}},["key"]="rash",["name"]="RASH",["navigation"]={2,4,4},["owner"]=33,["private_hook"]={["bank"]=3,["offset"]=28370,["pc"]=44754},["ram"]={["AreaAddrsLOffset"]=1876,["AreaPointer"]=1877,["AreaType"]=1875,["Block_Buffer_1"]=768,["BtHostReady"]=48992,["BtLife"]=48995,["BtSrc_FrameCounter"]=48864,["BtSrc_FrameCounter_Even"]=48865,["BtSrc_Objects_Life"]=48956,["BtSrc_Objects_death_timer"]=48968,["BtSrc_player1_obj_wanted_frame"]=48906,["BtVariant"]=48993,["CheatInvincible"]=32763,["CheatStartLevel"]=32764,["CrossoverBehaviorVersion"]=32737,["CrossoverMenuIndex"]=29449,["CrossoverMenuState"]=29447,["CrossoverTitleDrawn"]=24580,["CurrentCHRBank"]=327,["DisableScreenFlag"]=1909,["Enemy_Flag"]=16,["Enemy_ID"]=23,["Enemy_PageLoc"]=93,["Enemy_State"]=31,["Enemy_X_Position"]=118,["Enemy_Y_HighPos"]=165,["Enemy_Y_Position"]=190,["FmGroups"]=24552,["GameEngineSubroutine"]=15,["GuestPowerupActive"]=27645,["GuestPowerupAge"]=27646,["HpActorOwner"]=29614,["LevelNumber"]=1889,["MarioVariant"]=29450,["NmiSkipped"]=314,["NumberofLives"]=1887,["OperMode"]=1905,["OperMode_Task"]=1907,["PlatformCollisionFlag"]=1382,["PlayerFacingDir"]=1342,["PlayerStatus"]=1883,["Player_PageLoc"]=92,["Player_State"]=30,["Player_X_Position"]=117,["Player_X_Speed"]=70,["Player_Y_HighPos"]=164,["Player_Y_Position"]=189,["Player_Y_Speed"]=142,["PowerUpType"]=52,["PreviousA_B_Buttons"]=1371,["RcArea"]=24486,["RcAttack"]=23556,["RcAttackKind"]=23557,["RcCarrySlot"]=23569,["RcClock"]=23555,["RcHealth"]=24480,["RcHeld"]=23554,["RcHurt"]=23563,["RcLife"]=24485,["RcMarker"]=24484,["RcPose"]=23566,["RcPrevious"]=23552,["RcRun"]=23560,["RcSavedVariant"]=24488,["RcTier"]=24482,["RcVariant"]=24557,["RcWorld"]=24487,["SavedJoypadBits"]=220,["ScreenLeft_PageLoc"]=1821,["ScreenLeft_X_Pos"]=1823,["ScrollLock"]=1830,["SelectedCharacter"]=24578,["StarInvincibleTimer"]=1948,["TimerControl"]=1866,["WorldNumber"]=1892,["X5ChrMode"]=29664,["X5WideChrActive"]=29678},["sha"]="174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4",["slot"]=23,["variant"]=0}
local ROSTER_CONFIG={name="rash"}
local choose=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=near and e.dx<48 and c.poll%32<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true;b.b=false;if c.grounded and not c.lastA then b.a=true end end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()
-- Normal controller inputs and readonly native witnesses. No game-state writes.
local frame,polls,updates,entries,age=0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local buttons,finished,lastA={},false,false
local first,flag,castle,entrance
local nextUpdates,maxX=0,0
local pendingReturn
local checkpoints,menuEvents={},{}
local function r(n,i)local at=assert(C.ram[n],n)+(i or 0);if n:sub(1,2)=='Bt'then return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end;return emu.read(at,emu.memType.nesDebug)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function identity()return r('SelectedCharacter')==33 and (r('FmGroups')&32)==C.variant and r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0 end
local function state()return {frame=frame,Main=updates,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),state=r('Player_State'),engine=r('GameEngineSubroutine'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaType'),power=r('PlayerStatus'),source_HP=r('BtSrc_Objects_Life'),source_death_timer=r('BtSrc_Objects_death_timer'),source_pose=r('BtSrc_player1_obj_wanted_frame'),source_ready=r('BtHostReady'),lives=r('NumberofLives'),variant=r('BtVariant'),chr_mode=r('X5ChrMode'),star=r('StarInvincibleTimer')}end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local a={};if #v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(k)..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
end
local btMoves,btNext,btHeld,btDirty,btMin=0,0,0,false,255
local btInput,btDecide={},nil
local idleStart,idleEnd,walkStart,walkEnd
local idleActors=0
local portRead=false
local priorFrameMain=0
local readCounts={idle={frames=0,missed=0,Main_histogram={}},walk={frames=0,missed=0,Main_histogram={}}}
local function finish(reason)
 if finished then return end;finished=true
 local ok=reason=='idle48-walk32-observation'and first and idleStart and idleEnd and identity()and active()and r('NumberofLives')==2 and updates-idleStart.Main==80 and walkStart and walkEnd and idleActors==0

 print('SMB_NATIVE_RECEIPT '..json({passed=not not ok,reason=reason,ROM_SHA256=C.sha,identity=C.key,name=C.name,Select_cycle=C.cycle,BtVariant=C.variant,physical_frames=frame,input_polls=polls,Main_entries=entries,Main_returned=updates,Main_updates=updates,first_active=first,flag=flag,castle=castle,entrance=entrance,next_area_updates=nextUpdates,terminal=state(),max_x=maxX,checkpoints=checkpoints,menu_events=menuEvents,controller_read_observations=readCounts,walk_start=walkStart,walk_end=walkEnd,walk_Main_returns=walkStart and updates-walkStart.Main or -1,walk_physical_frames=walkStart and frame-walkStart.frame or -1,walk_NMI_skips=walkStart and(r('NmiSkipped')-walkStart.skips)&255 or -1,idle_start=idleStart,idle_end=idleEnd,idle_Main_returns=walkStart and walkStart.Main-idleStart.Main or -1,idle_physical_frames=walkStart and walkStart.frame-idleStart.frame or -1,idle_NMI_skips=walkStart and(walkStart.skips-idleStart.skips)&255 or -1,idle_max_active_actors=idleActors,scope='Optimized Rash idle48 then Right32 completed Main updates; real physical cadence; no stage-clear claim',Bt_source_steps=btMoves,Bt_1_2_steps=btNext,minimum_source_HP=btMin,private_state_read="physicalRAM3",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false,outputs=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if finished then return end;local ok,why=pcall(fn,...);if not ok then finish('callback-error:'..tostring(why))end end end
local function hook(name,fn)
 local h=C.hooks[name]
 emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesPrgRom or a.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact native hook '..name)end
  fn()
 end),emu.callbackType.exec,h.pc)
end

emu.addMemoryCallback(guard(function()portRead=true end),emu.callbackType.read,0x4016)
emu.addMemoryCallback(guard(function()portRead=true end),emu.callbackType.read,0x4017)
emu.addEventCallback(guard(function()
 if idleStart and frame>idleStart.frame and not walkEnd then
  local q=readCounts[walkStart and'walk'or'idle'];q.frames=q.frames+1
  if not portRead then q.missed=q.missed+1 end
  local key=tostring(updates-priorFrameMain);q.Main_histogram[key]=(q.Main_histogram[key]or 0)+1
 end
 portRead=false;priorFrameMain=updates
end),emu.eventType.endFrame)
emu.addMemoryCallback(guard(function()
 local h=C.private_hook;local a=emu.convertAddress(h.pc)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.offset then return end
 if first and active()and identity()then
  assert(r('BtHostReady')==1 and r('BtVariant')==C.variant,'Actual private RAM3 source identity')
  btMoves=btMoves+1;if r('LevelNumber')==1 then btNext=btNext+1 end
  btHeld=r('SavedJoypadBits');btDirty=true
 end
end),emu.callbackType.exec,C.private_hook.pc)
hook('GameLoop',function()
 assert(not pendingReturn,'Previous Main must return before another entry')
 local sp=emu.getState()['cpu.sp']
 local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 assert(ret==C.hooks.GameLoopReturn0.pc or ret==C.hooks.GameLoopReturn1.pc,'Exact compiled Main caller')
 entries=entries+1;pendingReturn={pc=ret,sp=(sp+2)&255}
end)
local function returned(pc)
 assert(pendingReturn and pendingReturn.pc==pc and pendingReturn.sp==emu.getState()['cpu.sp'],'Same Main caller/SP return')
 pendingReturn=nil;updates=updates+1
 if first and active()and identity()then
  idleStart=idleStart or{Main=updates,frame=frame,skips=r('NmiSkipped'),source_steps=btMoves}
  local actors=0;for i=0,5 do if r('Enemy_Flag',i)>0 then actors=actors+1 end end
  idleActors=math.max(idleActors,actors)
  if updates-idleStart.Main==48 then idleEnd=state();walkStart={Main=updates,frame=frame,skips=r('NmiSkipped'),source_steps=btMoves};btInput={right=true}end
  if updates-idleStart.Main==80 then walkEnd=state();finish('idle48-walk32-observation');return end
 end
 if first and active()and identity()then btMin=math.min(btMin,r('BtSrc_Objects_Life'))end
 if not(active()and identity())then btInput={}end
 if btDirty then btDirty=false;if btDecide then btDecide()end end
 if first and r('WorldNumber')==0 and r('LevelNumber')==1 and active()then
  if r('AreaType')==2 and r('Player_State')==0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<224 then
   nextUpdates=nextUpdates+1
   if nextUpdates==25 then finish('full-1-1-and25grounded-1-2')end
  else nextUpdates=0 end
 end
end
hook('GameLoopReturn0',function()returned(C.hooks.GameLoopReturn0.pc)end)
hook('GameLoopReturn1',function()returned(C.hooks.GameLoopReturn1.pc)end)
hook('FlagpoleRoutine',function()if first and not flag and identity()and r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 and pos('Player_X_Position','Player_PageLoc')>=3000 then flag=state()end end)
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,name)local began=frame;while not fn()and frame-began<limit do wait(1)end;assert(fn(),'Actual frontend '..name)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Explicit421 ROM pin')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Cold Easy/no cheats')
 press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 assert(r('CrossoverMenuIndex')==0 and r('SelectedCharacter')==0 and r('MarioVariant')==0,'Actual initial Mario')
 press('left');press('down');press('down')
 assert(r('CrossoverMenuIndex')==23 and r('SelectedCharacter')==33,'Actual Battletoads slot')
 for i=1,C.cycle do press('select');menuEvents[i]={frame=frame,variant=r('BtVariant'),raw=r('SelectedCharacter')}end
 assert(identity(),'Actual compiled alternate cycle')
 if C.key=='kamikaze'then assert(r('X5ChrMode')==0x84,'Actual Kamikaze skin publication')end
 press('start');menuDone=true
end)
local function context()
 local c={frame=btMoves,poll=btMoves,char=33,variant=C.variant,r=r,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=(btHeld&128)~=0,grounded=r('Player_State')==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16))end
 c.enemy=function()
  local nearest
  for i=0,5 do local id,st,f=r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_Flag',i)
   if f>0 and f<128 and(id<0x15 or id==0x2d or id==0x33)and st<32 and not(id==6 and st>=2)then
    local x=pos('Enemy_X_Position','Enemy_PageLoc',i);local dx=x-c.x
    if dx> -160 and dx<160 and(not nearest or math.abs(dx)<math.abs(nearest.dx))then nearest={slot=i,id=id,x=x,y=r('Enemy_Y_Position',i),state=st,dx=dx}end
   end
  end;return nearest
 end
 return c
end
btDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then btInput=walkStart and{right=true}or{}else btInput={}end
end
emu.addEventCallback(guard(function()
 polls=polls+1;local b=buttons
 if menuDone then b=btInput end
 lastA=not not b.a;emu.setInput(b,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 if not first and active()and r('WorldNumber')==0 and r('LevelNumber')==0 then
  assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 and r('BtHostReady')==1 and r('BtVariant')==C.variant and r('BtSrc_Objects_Life')==47,'Genuine initial Battletoads constructor')
  first=state()
 end
 if first then
  if not identity()or r('NumberofLives')~=2 or r('GameEngineSubroutine')==11 or r('OperMode')==3 then finish('identity-life-or-death');return end
  local s=state();maxX=math.max(maxX,s.x)
  if s.level==0 and s.x>=256+#checkpoints*256 and #checkpoints<13 then checkpoints[#checkpoints+1]=s end
  if s.world==0 and s.level==0 and s.engine==5 and s.x>=3160 then castle=castle or s end
  if s.world==0 and s.level==1 and s.engine==0 then entrance=entrance or s end
  if s.world~=0 or s.level>1 or(s.level==1 and not(flag and castle))then finish('shortcut-or-unexpected-stage');return end
 end
 if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end
end),emu.eventType.endFrame)
