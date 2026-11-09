local L,C=assert(MINI_FIREBALL_SYMBOLS),assert(MINI_FIREBALL_CONFIG)
assert(C.pool_slots==2,'Two native fireball slots required by this observer')
local frame,age,updates,done,checks,shots=0,0,0,false,0,0
local phase,variant='title',1
local phases,events,spawns,latestDraw={},{},{},nil
local coreCalls,draws,dmas,bounces,minimumSP=0,0,0,0,255
local coreBySlot,movedBySlot,bounceBySlot,spawnPending,last={0,0},{false,false},{0,0},{},{}
local maxActive,maxVisible,twoDraws,twoDMAs=0,0,0,0
local visibleByGroup,upward={right=0,left=0,up=0},false
local liveFrames,impactFrames={},{}
local impactTargetHit=false
local pending,returns=nil,{}
local initialLives,stable,groupStart=0,0,0
local cadence,readCounts,framePhase,previousUpdates,previousSkipped={}, {0,0},nil,0,nil
local plans={
 right={one=20,release=4,two=4,full_release=3,third=4,clear=180},
 left={one=4,release=2,two=4,clear=120},
 up={one=8,release=2,two=8,full_release=2,third=4,clear=180}}
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return read(assert(L[n],n))end
local function rs(n,slot)return read(assert(L[n],n)+slot)end
local function write(n,v)emu.write(assert(L[n],n),v&255,emu.memType.nesDebug)end
local function ram(a)return emu.read(2*8192+a-0xc000,emu.memType.nesWorkRam)end
local function groupStage()return phase:match('^(%a+)%-([%a%-]+)$')end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',k)..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return 'null'else return tostring(v)end
end
local function check(ok,why)checks=checks+1;assert(ok,why)end
local function active()return r('SelectedCharacter')==41 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and ram(0xc300)==2 end
local function shot(tag)
 if shots>=3 then return end;shots=shots+1
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function result(ok,why)
 local q={passed=ok,error=why,ROM_sha256=C.ROM_sha256,physical_frames=frame,native_Main=updates,
  checks=checks,phase=phase,phases=phases,events=events,spawns=spawns,core_calls=coreCalls,
  core_calls_by_slot=coreBySlot,movement_by_slot=movedBySlot,bounces_by_slot=bounceBySlot,
  draw_returns=draws,normal_DMAs=dmas,bounce_edges=bounces,max_active_fireballs=maxActive,
  max_visible_fireballs=maxVisible,two_fireball_draw_returns=twoDraws,two_fireball_DMAs=twoDMAs,
  concurrent_DMA_by_direction=visibleByGroup,upward_shot_observed=upward,
  phase_cadence=cadence,cadence_zero_lag_enforced=false,
  cadence_description='Per physical frame: actual $013A NmiSkipped delta, actual $4016/$4017 reads, and completed native GameCore deltas. Cold/menu boot phases excluded; lag is reported without weakening projectile behavior assertions.',
  minimum_hook_SP=minimumSP,screenshots=shots,
  fixture={used=true,after_cold_menu=true,initial_worldX=40,PlayerStatus=2,
   cleared_native_enemies=true,cleared_native_fireball_pool=true,
   description='Native power tier2 and empty native actor/projectile pools are seeded once after actual cold MiniReady2/engine8/floor handoff. Idle, movement, fresh/held B, two native actors, third-shot rejection, reversal, Up, bounce, clipping and OAM execute natively from real polled input.'},
  controller_only=false,earned_powerup_claim=false,enemy_kill_claim=false,full_stage=false,
  helpers_added=false,tile_extent=C.tile_extent,expected_projectile_palette=C.palette,
  moving_art_phases=liveFrames,impact_art_frames=impactFrames,staged_goomba_hit=impactTargetHit}
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\n');f:close()
end
local function guard(fn)return function(...)
 if done then return end;local ok,e=pcall(fn,...)
 if not ok then shot('mini-two-fireball-failure');result(false,tostring(e));done=true;print(tostring(e));emu.stop(1)end
end end
local function transition(p)
 if #events<64 then events[#events+1]={phase=p,frame=frame,update=updates,states={r('Fireball_State'),r('Fireball_State1')},x=r('Player_X_Position'),y=r('Player_Y_Position')}end
 phase=p;age=0
 if p=='right-one-hold'or p=='left-one-hold'or p=='up-one-hold'then groupStart=#spawns end
end
local function valid(h)
 local p=emu.convertAddress(h.pc)
 if not p or p.memType~=emu.memType[h.memory]or p.address~=h.physical then return false end
 for i,v in ipairs(h.bytes)do check(read(h.pc+i-1)==v,'Bound native hook '..h.name)end
 minimumSP=math.min(minimumSP,emu.getState()['cpu.sp']);return true
end
local function context()
 local s=emu.getState();local sp=s['cpu.sp'];local ret=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local a=assert(emu.convertAddress(ret));return{ret=ret,sp=(sp+2)&255,memory=a.memType,physical=a.address}
end
local function matches(q)
 local s=emu.getState();local a=emu.convertAddress(s['cpu.pc'])
 return s['cpu.pc']==q.ret and s['cpu.sp']==q.sp and a and a.memType==q.memory and a.address==q.physical
end
local function stateSample()
 check(r('NumberofLives')==initialLives,'Focused fixture preserves lives')
 local live,total=0,0
 for slot=0,1 do
  local state,x,y,vy,bounce=rs('Fireball_State',slot),rs('Fireball_X_Position',slot)+256*rs('Fireball_PageLoc',slot),rs('Fireball_Y_Position',slot),rs('Fireball_Y_Speed',slot),rs('FireballBouncingFlag',slot)
  local old=last[slot]or{};local bounced=bounce~=0 and(old.bounce or 0)==0
  if state==1 then live=live+1 end;if state~=0 then total=total+1 end
  if state==1 and old.state==1 then
   if x~=old.x or y~=old.y then movedBySlot[slot+1]=true end
   if old.vy and old.vy<128 and vy>=128 then bounced=true end
  end
  if bounced then bounces=bounces+1;bounceBySlot[slot+1]=bounceBySlot[slot+1]+1 end
  local animation=C.phase_ram and ram(C.phase_ram[slot+1])or 0
  if C.phase_ram then
   local tick=state==1 and r('FrameCounter')&3==0 and 1 or 0
   check(animation==(((old.animation or 0)+tick)&255),'Per-slot source artwork advances every fourth active update')
  end
  last[slot]={state=state,x=x,y=y,vy=vy,bounce=bounce,animation=animation}
 end
 maxActive=math.max(maxActive,live);check(live<=2,'Native two-shot capacity bound')
 return live,total
end
local function addImpactTarget()
 local slot=5
 local x=r('Player_X_Position')+256*r('Player_PageLoc')+22
 local fields={Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x&255,Enemy_PageLoc=x//256,
  Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_X_Speed=248,Enemy_MovingDir=2,Enemy_BoundBoxCtrl=9}
 for name,value in pairs(fields)do emu.write(assert(L[name])+slot,value,emu.memType.nesDebug)end
end
local function sample()
 updates=updates+1;age=age+1
 if phase=='game'then
  if r('Player_State')==0 and r('Player_Y_Speed')==0 and ram(0xc246)==2 and ram(0xc24c)&1~=0 then stable=stable+1 else stable=0 end
  if stable>=4 then
   check(r('Player_X_Position')+256*r('Player_PageLoc')==40,'Actual initial worldX40 before fixture')
   initialLives=r('NumberofLives')
   write('PlayerStatus',2);write('Fireball_State',0);write('Fireball_State1',0)
   write('FireballMetasprite',0);write('FireballMetasprite1',0)
   for i=0,5 do emu.write(L.Enemy_Flag+i,0,emu.memType.nesDebug)end
   transition('idle')
  end
  return
 end
 if phase=='title'or phase=='open'or phase=='select'or phase=='confirm'then return end
 check(active(),'Mini stays active during explicit fixture')
 local live,total=stateSample();local q=phases[phase]or{updates=0,peak_live=0}
 phases[phase]=q;q.updates=q.updates+1;q.peak_live=math.max(q.peak_live,live)
 if phase=='idle'then
  check(total==0,'Idle begins with an empty native two-shot pool')
  if age>=60 then transition('right-one-hold')end
  return
 elseif phase=='face-left'then
  if age>=2 then check(r('PlayerFacingDir')==2,'Controller establishes native left facing');transition('left-one-hold')end
  return
 elseif phase=='face-right'then
  if age>=2 then check(r('PlayerFacingDir')==1,'Controller establishes native right facing');transition('up-one-hold')end
  return
 elseif phase=='impact'then
  if rs('Enemy_State',5)&32~=0 then impactTargetHit=true end
  if impactFrames.C and impactFrames.D and impactTargetHit and total==0 then transition('finish')end
  check(age<100,'Actual Goomba defeat and both original impact tiles must reach normal DMA')
  return
 end
 local group,stage=groupStage();local plan=plans[group]
 if not plan then return end
 local count=#spawns-groupStart
 if stage=='one-hold'then
  check(count<=1,'Held B cannot emit a second shot')
  if age>=plan.one then check(count==1 and live==1,'First fresh B makes exactly one live native shot');transition(group..'-release')end
 elseif stage=='release'then
  if age>=plan.release then check(live==1,'First shot stays live before second fresh B');transition(group..'-two-hold')end
 elseif stage=='two-hold'then
  check(count<=2,'Held second B cannot emit a series')
  if age>=plan.two then
   check(count==2,'Second fresh B creates the other native slot')
   local a,b=spawns[groupStart+1],spawns[groupStart+2]
   check(a.slot~=b.slot,'Two fresh shots use distinct native actor slots')
   check(live==2,'Two native fireballs are concurrently active')
   transition(group..(plan.third and'-full-release'or'-clear'))
  end
 elseif stage=='full-release'then
  if age>=plan.full_release then check(live==2,'Both slots remain busy before third fresh B');transition(group..'-third-hold')end
 elseif stage=='third-hold'then
  check(count==2,'Third fresh B is blocked while both native slots are busy')
  check(live==2,'Third-shot rejection is observed with both slots actually live')
  if age>=plan.third then transition(group..'-clear')end
 elseif stage=='clear'then
  check(age<plan.clear,'Native '..group..' terrain/clipping completion bound')
  if total==0 then
   check(count==2,'Exactly two shots in '..group..' group')
   check(visibleByGroup[group]>0,'Two distinct OAM records reached actual '..group..' normal DMA')
   if group=='right'then
    check(movedBySlot[1]and movedBySlot[2]and bounceBySlot[1]>0 and bounceBySlot[2]>0,'Both native actors moved and bounced on actual terrain')
    transition('face-left')
   elseif group=='left'then transition('face-right')
   else
    check(#spawns==6 and upward,'Exactly six real-input shots across right/left/Up')
    check(coreBySlot[1]>0 and coreBySlot[2]>0,'Actual native Core executes independently for X0 and X1')
    check(maxActive==2 and maxVisible==2 and twoDMAs>0,'Two active fireballs and two concurrent normal-DMA records verified')
    if C.donor_frames then
     for i=0,3 do check(liveFrames[tostring(i)],'All four original moving phases reached DMA')end
     addImpactTarget()
     transition('impact')
    else
     transition('finish')
    end
   end
  end
 end
end

local core=C.hooks.FireballObjCore
emu.addMemoryCallback(guard(function()
 if not active()or not valid(core)then return end
 local slot=emu.getState()['cpu.x'];check(slot==0 or slot==1,'Actual native Core actor index0/1')
 if rs('Fireball_State',slot)==0 then return end
 coreCalls=coreCalls+1;coreBySlot[slot+1]=coreBySlot[slot+1]+1
 if spawnPending[slot]then
  spawnPending[slot]=nil
  local left=r('PlayerFacingDir')==2;local px=r('Player_X_Position')+256*r('Player_PageLoc')
  local bx=rs('Fireball_X_Position',slot)+256*rs('Fireball_PageLoc',slot)
  check(bx==px+(left and C.spawn_left or C.spawn_right),'Native spawn base preserves requested visible launch X')
  check(rs('Fireball_Y_Position',slot)==((r('Player_Y_Position')+20)&255),'Native spawn base Y is source Mario canvas')
  check(rs('Fireball_BoundBoxCtrl',slot)==8,'Actual native ctrl8 4x4 collision box for each slot')
  check(rs('Fireball_X_Speed',slot)==(left and 224 or 32),'Native signed horizontal speed')
  local group=groupStage();local up=group=='up'
  check(rs('Fireball_Y_Speed',slot)==(up and 255 or 1),'Source Down/Up initial native vertical speed')
  if up then upward=true end
  spawns[#spawns+1]={frame=frame,update=updates,phase=phase,slot=slot,left=left,baseX=bx,
   baseY=rs('Fireball_Y_Position',slot),visibleX=bx+C.draw_x,visibleY=rs('Fireball_Y_Position',slot)+C.draw_y,
   xSpeed=rs('Fireball_X_Speed',slot),ySpeed=rs('Fireball_Y_Speed',slot),ctrl=rs('Fireball_BoundBoxCtrl',slot)}
 end
end),emu.callbackType.exec,core.pc)
for slot=0,1 do local ownedSlot=slot
 emu.addMemoryCallback(guard(function(_,v)
  if not active()or phase=='game'or v~=1 then return end
  local a=emu.convertAddress(emu.getState()['cpu.pc'])
  if not a or a.memType~=emu.memType.nesPrgRom or not C.spawn_banks[a.address//8192]then return end
  check(not spawnPending[ownedSlot],'One synchronous constructor per native slot')
  spawnPending[ownedSlot]=true
 end),emu.callbackType.write,L.Fireball_State+ownedSlot)
end

local draw=C.hooks.MiniFireballDraw;local drawPending=nil;local drawReturns={}
local function spriteRecord(slot,x,y,state)
 local tile,attribute,yOffset=0x6f,2,C.draw_y-1
 local frameName,phase
 if C.donor_frames then
  if state==1 then
   phase=ram(C.phase_ram[slot+1])&3
   frameName=(phase&1==0)and'A'or'B'
   if phase>=2 then attribute=0xc2;yOffset=yOffset-8 end
  else
   frameName=(state&2==0)and'C'or'D'
  end
  tile=C.donor_frames[frameName].tile
 end
 return {tile=tile,attribute=attribute,x=(x+C.draw_x)&255,y=(y+yOffset)&255,
         frameName=frameName,phase=phase,live=state==1}
end
local function sameRecord(at,part)
 return read(at)==part.y and read(at+1)==part.tile and read(at+2)==part.attribute and read(at+3)==part.x
end
emu.addMemoryCallback(guard(function()
 if not active()or not valid(draw)then return end
 local q=context();q.parts={};q.logical=r('CurrentOAMOffset');q.group=groupStage();q.live=0
 local logical=q.logical;local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 for slot=0,1 do
  local x=rs('Fireball_X_Position',slot)-r('ScreenLeft_X_Pos')
  local y=rs('Fireball_Y_Position',slot);local page=rs('Fireball_PageLoc',slot)-r('ScreenLeft_PageLoc')
  local state=rs('Fireball_State',slot)
  local allowed=state==1 or (C.donor_frames and state>=0x80 and state<0x86)
  if allowed and logical<252 and page==0 and x>=0 and x<C.draw_limit and y<236 and (not C.donor_frames or y>=8) then
   local part=spriteRecord(slot,x,y,state);part.actor=slot;part.slot=(logical+rotation)&255
   q.parts[#q.parts+1]=part;logical=logical+4
   if part.live then q.live=q.live+1 end
  end
 end
 drawPending=q
 if not drawReturns[q.ret]then drawReturns[q.ret]=true;emu.addMemoryCallback(guard(function()
  if drawPending and matches(drawPending)then
   local p=drawPending;drawPending=nil;draws=draws+1;latestDraw=nil
   check(r('CurrentOAMOffset')==p.logical+#p.parts*4,'Each admitted native shot reserves its own four OAM bytes')
   for _,part in ipairs(p.parts)do
    check(sameRecord(0x200+part.slot,part),'Each exact projectile OAM tile, attribute and position')
   end
   if p.live==2 then
    check(p.parts[1].slot~=p.parts[2].slot,'Two native shots have distinct OAM records')
    check(p.parts[1].x~=p.parts[2].x or p.parts[1].y~=p.parts[2].y,'Staggered shots render independent projectile positions')
    twoDraws=twoDraws+1
   end
   maxVisible=math.max(maxVisible,p.live)
   if #p.parts>0 then latestDraw=p end
  end
 end),emu.callbackType.exec,q.ret)end
end),emu.callbackType.exec,draw.pc)
emu.addMemoryCallback(guard(function(_,page)
 if not active()or not latestDraw then return end;dmas=dmas+1
 local s=emu.getState()
 check(s['mapper.chrBanks5']==967,'Published projectile CHR slot5=physical967')
 check(s['mapper.chrMode']==3 and s['ppu.control.largeSprites']==true,'MMC5 1KB spritebank and 8x16 sprite mode')
 local frames=C.donor_frames or {A={offset=0x2e0,data=C.art}}
 for _,art in pairs(frames)do
  for i,v in ipairs(art.data)do check(emu.read(967*1024+art.offset+i-1,emu.memType.nesChrRom)==v,'Exact physical sprite art')end
 end
 for i,v in ipairs(C.palette)do check(emu.read(0x3f18+i,emu.memType.nesPpuDebug)==v,'Actual warm native spritepalette2 red/white/orange')end
 local p=latestDraw
 for _,part in ipairs(p.parts)do
  check(sameRecord(page*256+part.slot,part),'Actual normal DMA contains each independent native projectile record')
  if part.phase then liveFrames[tostring(part.phase)]=true
  elseif part.frameName then impactFrames[part.frameName]=true end
 end
 if p.live==2 then twoDMAs=twoDMAs+1;if visibleByGroup[p.group]then visibleByGroup[p.group]=visibleByGroup[p.group]+1 end end
 local mini=false;for at=page*256,page*256+252,4 do if read(at)<240 and read(at+1)%2==1 and read(at+1)<64 then mini=true end end
 check(mini,'Actual DMA includes Mini body beside native projectiles')
end),emu.callbackType.write,0x4014)

local main=C.hooks.GameCoreRoutine
emu.addMemoryCallback(guard(function()
 if not active()or not valid(main)then return end
 if not framePhase then framePhase=phase end
 check(not pending,'Synchronous actual native Main');pending=context();local ret=pending.ret
 if not returns[ret]then returns[ret]=true;emu.addMemoryCallback(guard(function()
  if pending and matches(pending)then pending=nil;if active()then sample()end end
 end),emu.callbackType.exec,ret)end
end),emu.callbackType.exec,main.pc)
for port=0,1 do local ownedPort=port
 emu.addMemoryCallback(guard(function()readCounts[ownedPort+1]=readCounts[ownedPort+1]+1;if not framePhase then framePhase=phase end end),emu.callbackType.read,0x4016+ownedPort)
end
emu.addEventCallback(guard(function()
 local keys={};local group,stage=groupStage()
 if phase=='open'and age<6 then keys.start=true
 elseif phase=='select'and age<6 then keys.select=true
 elseif phase=='confirm'and age<6 then keys.start=true
 elseif plans[group]and(stage=='one-hold'or stage=='two-hold'or stage=='third-hold')then keys.b=true;if group=='up'then keys.up=true end
 elseif phase=='face-left'then keys.left=true
 elseif phase=='face-right'then keys.right=true
 elseif phase=='impact'and age<4 then keys.b=true end
 emu.setInput(keys,0)
end),emu.eventType.inputPolled)
local pictured={}
emu.addEventCallback(guard(function()
 frame=frame+1
 local skipped=r('NmiSkipped');local delta=previousSkipped and((skipped-previousSkipped)&255)or 0
 local observedPhase=framePhase or phase
 if observedPhase~='title'and observedPhase~='open'and observedPhase~='select'and observedPhase~='confirm'and observedPhase~='game'then
  local q=cadence[observedPhase]or{video_frames=0,native_updates=0,lag_nmi=0,no_controller_read=0,controller_reads4016=0,controller_reads4017=0,max_updates_per_frame=0}
  local changed=updates-previousUpdates;q.video_frames=q.video_frames+1;q.native_updates=q.native_updates+changed
  q.lag_nmi=q.lag_nmi+delta;q.no_controller_read=q.no_controller_read+((readCounts[1]+readCounts[2]==0)and 1 or 0)
  q.controller_reads4016=q.controller_reads4016+readCounts[1];q.controller_reads4017=q.controller_reads4017+readCounts[2]
  q.max_updates_per_frame=math.max(q.max_updates_per_frame,changed);cadence[observedPhase]=q
 end
 previousSkipped=skipped;previousUpdates=updates;readCounts={0,0};framePhase=nil
 check(frame<C.max_frames,'Bounded focused two-fireball native run')
 if phase=='title'or phase=='open'or phase=='select'or phase=='confirm'or phase=='game'then age=age+1 end
 if phase=='title'and frame>=120 then check(r('OperMode')==0,'Actual cold title');transition('open')
 elseif phase=='open'and age>=70 then check(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Actual initial Mario slot');transition('select')
 elseif phase=='select'and age>=35 then
  check(r('MarioVariant')==C.menu_variants[variant],'Actual Mini Select cycle')
  if variant<8 then variant=variant+1;age=0 else check(r('SelectedCharacter')==41,'Actual Mini selected');transition('confirm')end
 elseif phase=='confirm'and age>=8 then transition('game')
 elseif phase=='game'then check(age<700,'Actual cold MiniReady2 floor handoff bound')
 elseif phase=='finish'then result(true);done=true;print('PASS focused native Mini two-fireball fixture');emu.stop(0)
 elseif latestDraw and latestDraw.live==2 and latestDraw.group and not pictured[latestDraw.group]then pictured[latestDraw.group]=true;shot('mini-two-fireballs-'..latestDraw.group)end
end),emu.eventType.endFrame)
