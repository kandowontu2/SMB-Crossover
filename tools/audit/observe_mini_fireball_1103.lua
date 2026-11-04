local L,C=assert(MINI_FIREBALL_SYMBOLS),assert(MINI_FIREBALL_CONFIG)
local frame,age,updates,done,checks,shots=0,0,0,false,0,0
local phase,variant='title',1
local phases,events,spawns,latestDraw={},{},{},nil
local coreCalls,draws,dmas,bounces,minimumSP=0,0,0,0,255
local spawnPending,pending,returns=false,nil,{}
local lastState,lastYSpeed,lastX,lastY,lastBounce=0,nil,nil,nil,0
local initialLives,shotStart,moved,upward,stable=0,0,false,false,0
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return read(assert(L[n],n))end
local function write(n,v)emu.write(assert(L[n],n),v&255,emu.memType.nesDebug)end
local function ram(a)return emu.read(2*8192+a-0xc000,emu.memType.nesWorkRam)end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',k)..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return 'null'else return tostring(v)end
end
local function check(ok,why)checks=checks+1;assert(ok,why)end
local function active()return r('SelectedCharacter')==41 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and ram(0xc300)==2 end
local function shot(tag)
 if shots>=4 then return end;shots=shots+1
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function result(ok,why)
 local q={passed=ok,error=why,ROM_sha256=C.ROM_sha256,physical_frames=frame,native_Main=updates,
  checks=checks,phase=phase,phases=phases,events=events,spawns=spawns,core_calls=coreCalls,
  draw_returns=draws,normal_DMAs=dmas,bounce_edges=bounces,movement_observed=moved,
  upward_shot_observed=upward,minimum_hook_SP=minimumSP,screenshots=shots,
  fixture={used=true,after_cold_menu=true,initial_worldX=40,PlayerStatus=2,
   cleared_native_enemies=true,cleared_native_fireball_pool=true,
   description='Native power tier2 and empty native actor/projectile pools are seeded once after actual cold MiniReady2/engine8/floor handoff. Movement, firing, hold, reversal, Up, bounce, clipping and OAM execute natively from real polled controller input.'},
  controller_only=false,earned_powerup_claim=false,enemy_kill_claim=false,full_stage=false,
  helpers_added=false,tile_extent=C.tile_extent,expected_projectile_palette=C.palette}
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\n');f:close()
end
local function guard(fn)return function(...)
 if done then return end;local ok,e=pcall(fn,...)
 if not ok then shot('mini-fireball-failure');result(false,tostring(e));done=true;print(tostring(e));emu.stop(1)end
end end
local function transition(p)
 if #events<64 then events[#events+1]={phase=p,frame=frame,update=updates,state=r('Fireball_State'),x=r('Player_X_Position'),y=r('Player_Y_Position')}end
 phase=p;age=0;shotStart=#spawns
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
 check(r('Fireball_State1')==0,'Only slot0 belongs to Mini single-projectile pool')
 check(r('NumberofLives')==initialLives,'Focused fixture preserves lives')
 local state,x,y,vy,bounce=r('Fireball_State'),r('Fireball_X_Position')+256*r('Fireball_PageLoc'),r('Fireball_Y_Position'),r('Fireball_Y_Speed'),r('FireballBouncingFlag')
 local bounced=bounce~=0 and lastBounce==0
 if state==1 and lastState==1 then
  if x~=lastX or y~=lastY then moved=true end
  if lastYSpeed and lastYSpeed<128 and vy>=128 then bounced=true end
 end
 if bounced then bounces=bounces+1 end
 lastState,lastX,lastY,lastYSpeed,lastBounce=state,x,y,vy,bounce
 return state
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
   transition('right-hold')
  end
  return
 end
 if phase=='title'or phase=='open'or phase=='select'or phase=='confirm'then return end
 check(active(),'Mini stays active during explicit fixture')
 local state=stateSample();local q=phases[phase]or{updates=0,peak_live=0}
 phases[phase]=q;q.updates=q.updates+1;q.peak_live=math.max(q.peak_live,state==1 and 1 or 0)
 if phase=='right-hold'then
  check(#spawns<=1,'Held B never emits a second projectile')
  if age>=20 then check(#spawns==1 and state==1,'First fresh B makes one continuing native projectile');transition('right-release')end
 elseif phase=='right-release'then
  if age>=4 then check(state==1,'First projectile remains live before second fresh B');transition('right-busy-press')end
 elseif phase=='right-busy-press'then
  check(#spawns==1,'Fresh B while slot0 busy cannot create another shot')
  if age>=4 then transition('right-clear')end
 elseif phase=='right-clear'then
  check(age<180,'Right native terrain/clipping completion bound')
  if state==0 then check(moved and bounces>0,'Native movement and floor bounce observed');transition('face-left')end
 elseif phase=='face-left'then
  if age>=8 then check(r('PlayerFacingDir')==2,'Controller establishes native left facing');transition('left-hold')end
 elseif phase=='left-hold'then
  check(#spawns<=shotStart+1,'Held left B cannot emit a series')
  if age>=20 then check(#spawns==shotStart+1,'Fresh left-facing B creates exactly one native shot');transition('left-clear')end
 elseif phase=='left-clear'then
  check(age<120,'Left native clipping completion bound');if state==0 then transition('face-right')end
 elseif phase=='face-right'then
  if age>=8 then check(r('PlayerFacingDir')==1,'Controller establishes native right facing');transition('up-hold')end
 elseif phase=='up-hold'then
  check(#spawns<=shotStart+1,'Held Up+B cannot emit a series')
  if age>=12 then check(#spawns==shotStart+1 and upward,'Fresh Up+B uses upward native initial speed');transition('up-clear')end
 elseif phase=='up-clear'then
  check(age<180,'Up native terrain/clipping completion bound')
  if state==0 then
   check(#spawns==3,'Exactly three fixture shots across right/left/Up')
   check(draws>6 and dmas>6,'4x4 projectile rendered alongside Mini in actual normal DMA')
   transition('finish')
  end
 end
end

local core=C.hooks.FireballObjCore
emu.addMemoryCallback(guard(function()
 if not active()or not valid(core)then return end
 local slot=emu.getState()['cpu.x']
 if slot~=0 then check(read(L.Fireball_State+slot)==0,'No live secondary native projectile');return end
 if r('Fireball_State')==0 then return end
 coreCalls=coreCalls+1
 if spawnPending then
  spawnPending=false
  local left=r('PlayerFacingDir')==2;local px=r('Player_X_Position')+256*r('Player_PageLoc')
  local bx=r('Fireball_X_Position')+256*r('Fireball_PageLoc')
  check(bx==px+(left and C.spawn_left or C.spawn_right),'Native spawn base preserves requested visible launch X')
  check(r('Fireball_Y_Position')==((r('Player_Y_Position')+20)&255),'Native spawn base Y is source Mario canvas')
  check(r('Fireball_BoundBoxCtrl')==8,'Actual native ctrl8 4x4 collision box')
  check(r('Fireball_X_Speed')==(left and 224 or 32),'Native signed horizontal speed')
  local up=phase=='up-hold'
  check(r('Fireball_Y_Speed')==(up and 255 or 1),'Source Down/Up initial native vertical speed')
  if up then upward=true end
  spawns[#spawns+1]={frame=frame,update=updates,phase=phase,left=left,baseX=bx,
   baseY=r('Fireball_Y_Position'),visibleX=bx+C.draw_x,visibleY=r('Fireball_Y_Position')+C.draw_y,
   xSpeed=r('Fireball_X_Speed'),ySpeed=r('Fireball_Y_Speed'),ctrl=r('Fireball_BoundBoxCtrl')}
 end
end),emu.callbackType.exec,core.pc)
emu.addMemoryCallback(guard(function(_,v)
 if not active()or phase=='game'then return end
 if v==1 then
  local a=emu.convertAddress(emu.getState()['cpu.pc'])
  if not a or a.memType~=emu.memType.nesPrgRom or a.address//8192~=C.fire_bank then return end
  check(not spawnPending,'One synchronous projectile constructor');spawnPending=true
 end
end),emu.callbackType.write,L.Fireball_State)

local draw=C.hooks.MiniFireballDraw;local drawPending=nil;local drawReturns={}
emu.addMemoryCallback(guard(function()
 if not active()or not valid(draw)then return end
 local q=context();q.live=r('Fireball_State')==1;q.x=r('Fireball_X_Position')-r('ScreenLeft_X_Pos')
 q.y=r('Fireball_Y_Position');q.page=r('Fireball_PageLoc')-r('ScreenLeft_PageLoc')
 q.admitted=r('CurrentOAMOffset')<252
 q.slot=(r('CurrentOAMOffset')+(r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0))&255
 drawPending=q
 if not drawReturns[q.ret]then drawReturns[q.ret]=true;emu.addMemoryCallback(guard(function()
  if drawPending and matches(drawPending)then
   local p=drawPending;drawPending=nil;draws=draws+1;latestDraw=nil
   if p.live and p.admitted and p.page==0 and p.x>=0 and p.x<C.draw_limit and p.y<236 and p.slot<=252 then
    local a=0x200+p.slot
    check(read(a+1)==0x6f and read(a+2)==2,'Actual one-part4x4 projectile OAM tile/attribute')
    check(read(a+3)==((p.x+C.draw_x)&255)and read(a)==((p.y+C.draw_y-1)&255),'Actual 4x4 opaque origin matches corrected collision box')
    latestDraw=p
   end
  end
 end),emu.callbackType.exec,q.ret)end
end),emu.callbackType.exec,draw.pc)
emu.addMemoryCallback(guard(function(_,page)
 if not active()or not latestDraw then return end;dmas=dmas+1
 local s=emu.getState()
 check(s['mapper.chrBanks5']==967,'Published projectile CHR slot5=physical967')
 check(s['mapper.chrMode']==3 and s['ppu.control.largeSprites']==true,'MMC5 1KB spritebank and 8x16 sprite mode')
 for i,v in ipairs(C.art)do check(emu.read(967*1024+0x2e0+i-1,emu.memType.nesChrRom)==v,'Exact physical 4x4 sprite art')end
 for i,v in ipairs(C.palette)do check(emu.read(0x3f18+i,emu.memType.nesPpuDebug)==v,'Actual warm native spritepalette2 red/white/orange')end
 local p=latestDraw;local a=page*256+p.slot
 check(read(a+1)==0x6f and read(a+3)==((p.x+C.draw_x)&255),'Actual normal DMA contains native projectile record')
 local mini=false;for at=page*256,page*256+252,4 do if read(at)<240 and read(at+1)%2==1 and read(at+1)<64 then mini=true end end
 check(mini,'Actual DMA includes Mini body beside native projectile')
end),emu.callbackType.write,0x4014)

local main=C.hooks.GameCoreRoutine
emu.addMemoryCallback(guard(function()
 if not active()or not valid(main)then return end
 check(not pending,'Synchronous actual native Main');pending=context();local ret=pending.ret
 if not returns[ret]then returns[ret]=true;emu.addMemoryCallback(guard(function()
  if pending and matches(pending)then pending=nil;if active()then sample()end end
 end),emu.callbackType.exec,ret)end
end),emu.callbackType.exec,main.pc)
emu.addEventCallback(guard(function()
 local keys={}
 if phase=='open'and age<6 then keys.start=true
 elseif phase=='select'and age<6 then keys.select=true
 elseif phase=='confirm'and age<6 then keys.start=true
 elseif phase=='right-hold'or phase=='right-busy-press'or phase=='left-hold'then keys.b=true
 elseif phase=='face-left'then keys.left=true
 elseif phase=='face-right'then keys.right=true
 elseif phase=='up-hold'then keys.b=true;keys.up=true end
 emu.setInput(keys,0)
end),emu.eventType.inputPolled)
local pictured={}
emu.addEventCallback(guard(function()
 frame=frame+1
 check(frame<C.max_frames,'Bounded focused native fireball run')
 if phase=='title'or phase=='open'or phase=='select'or phase=='confirm'or phase=='game'then age=age+1 end
 if phase=='title'and frame>=120 then check(r('OperMode')==0,'Actual cold title');transition('open')
 elseif phase=='open'and age>=70 then check(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Actual initial Mario slot');transition('select')
 elseif phase=='select'and age>=35 then
  check(r('MarioVariant')==C.menu_variants[variant],'Actual Mini Select cycle')
  if variant<8 then variant=variant+1;age=0 else check(r('SelectedCharacter')==41,'Actual Mini selected');transition('confirm')end
 elseif phase=='confirm'and age>=8 then transition('game')
 elseif phase=='game'then check(age<700,'Actual cold MiniReady2 floor handoff bound')
 elseif phase=='finish'then result(true);done=true;print('PASS focused native Mini4x4 fireball fixture');emu.stop(0)
 elseif latestDraw and not pictured[phase]and(phase=='right-hold'or phase=='left-hold'or phase=='up-hold')then pictured[phase]=true;shot('mini-fireball-'..phase)end
end),emu.eventType.endFrame)
