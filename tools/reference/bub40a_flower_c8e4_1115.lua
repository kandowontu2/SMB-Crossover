local F={CrossoverTitleDrawn=24580,DisableScreenFlag=1909,CrossoverMenuState=29447,CrossoverMenuIndex=29449,SelectedCharacter=24578,OperMode=1905,OperMode_Task=1907,GameEngineSubroutine=15,NumberofLives=1887,Player_X_Position=117,Player_PageLoc=92,Player_Y_Position=189,GameLoop=33497,IdleLoop=33458,Enemy_Flag=16,Enemy_ID=23,Enemy_X_Position=118,Enemy_PageLoc=93,Enemy_Y_Position=190,NmiSkipped=314}
local Stock={["ram"]={["PowerUpType"]=52,["BoundingBox_UL_Corner"]=1624,["EnemyBoundingBoxCoord"]=1628,["Player1ScoreDisplay"]=1967,["FloateyNum_Control"]=269,["FloateyNum_Timer"]=297,["Square2SoundQueue"]=260,["GuestPowerupAge"]=27646,["GuestPowerupActive"]=27645},["hooks"]={["BbNativePickup"]={["pc"]=45665,["kind"]=1,["offset"]=29281,["data"]="08488a489848b534"},["BbNativeUpdate"]={["pc"]=48737,["kind"]=1,["offset"]=32353,["data"]="202cb6b001602018"},["BbGrantAfter"]={["pc"]=45698,["kind"]=1,["offset"]=29314,["data"]="68a868aa68288d6a"},["EraseEnemyObject"]={["pc"]=36143,["kind"]=2,["offset"]=1035567,["data"]="a90095109517951f"},["SetupFloateyNumber"]={["pc"]=39093,["kind"]=2,["offset"]=1038517,["data"]="8d6a01a9c08d6c01"},["GuestPowerupUpdate"]={["pc"]=45721,["kind"]=2,["offset"]=86681,["data"]="adfd6bf069ade17f"}},["identity"]=0,["ROM_SHA256"]="40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e"}
F.Block_Buffer_1=768
F.EnemyMetasprite=1762
F.Enemy_Flag=16
F.Enemy_ID=23
F.Enemy_MovingDir=1343
F.Enemy_PageLoc=93
F.Enemy_State=31
F.Enemy_X_Position=118
F.Enemy_X_Speed=71
F.Enemy_Y_Position=190
F.Enemy_Y_Speed=143
F.GameEngineSubroutine=15
F.GuestPowerupActive=27645
F.LevelNumber=1889
F.NumberofLives=1887
F.OperMode=1905
F.PlayerStatus=1883
F.Player_PageLoc=92
F.Player_State=30
F.Player_X_Position=117
F.Player_Y_HighPos=164
F.Player_Y_Position=189
F.SavedJoypadBits=220
F.ScreenLeft_PageLoc=1821
F.ScreenLeft_X_Pos=1823
F.SelectedCharacter=24578
F.WorldNumber=1892
local identity,expectedRom,cookie=0,"40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e","a72702dac1da2fc79faa02b5b5381392"
local hooks={{kind="rom",pc=33497,offset=1032921,data="a9ff8d3901205683"},{kind="rom",pc=33458,offset=1032882,data="ad3901f0fbad3a014820d98268cd3a01f0ee20c4edb0e9ad3a014820d98268a9008d3b014cb282"},{kind="work",pc=48737,offset=32353,data="202cb6b001602018"},{kind="work",pc=41298,offset=24914,data="ee1fc0a227a02bde"},{kind="work",pc=48404,offset=32020,data="08488a489848a200"}}
local sourcePc=41298
local returnPcs={33470,33488}

local frame,updates,sourceUpdates,pad,physicalPolls=0,0,0,0,0
local polled,game,done=false,false,false
local phase,pending,start,last,sourceThisMain='menu',nil,nil,nil,0
local phases={};local firstEnemy=nil
local enteredMain,sourceOutside=0,0;local returns={};local entries={}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n)return read(assert(F[n],n))end
local function work(bank,at)return emu.read(bank*8192+(at&8191),emu.memType.nesWorkRam)end
local function active()return r('SelectedCharacter')==39 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{frame=frame,updates=updates,source_updates=sourceUpdates,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),identity=work(2,0xc300)}end
local function encode(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=encode(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..encode(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local routeResult=nil
local flower={phase='mushroom',age=0,last=-1,takeoffs={},growth={},trajectory={},pipe_events={},rearm_requests=0,rearm_admissions=0}
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=reason,ROM_SHA256=expectedRom,name=identity==0 and 'BUB'or'BOB',controller_only=true,runtime_state_writes=0,capture_files=0,physical_frames=frame,Main_updates=updates,source_updates=sourceUpdates,entered_Main=enteredMain,returned_Main_histogram=returns,entry_return_histogram=entries,source_outside_pending=sourceOutside,phases=phases,first_enemy=firstEnemy,terminal=state(),route=routeResult,natural_flower=flower}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function mapped(pc,kind,offset)local a=emu.convertAddress(pc);return a and a.memType==kind and a.address==offset end
local function header(bank)local out={};for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',work(bank,at))end;return table.concat(out)end
local function actors()
 local out={}
 for slot=0,5 do local flag=read(F.Enemy_Flag+slot);if flag~=0 then out[#out+1]={slot=slot,flag=flag,id=read(F.Enemy_ID+slot),x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(F.Enemy_Y_Position+slot)}end end;return out
end
local function begin(name,bits)
 phase=name;pad=bits;start={state=state(),polls=physicalPolls,lag=r('NmiSkipped')};last=state()
end
local function close()
 local s=state();assert(s.updates-start.state.updates==s.source_updates-start.state.source_updates,'Every measured source opportunity has a completed Main')
 phases[phase]={physical_frames=s.frame-start.state.frame,Main_updates=s.updates-start.state.updates,source_updates=s.source_updates-start.state.source_updates,input_polled_frames=physicalPolls-start.polls,lag_NMI=(r('NmiSkipped')-start.lag)&255,initial=start.state,terminal=s,empty_actor_windows=true}
end
local L={["Block_Buffer_1"]=768,["EnemyMetasprite"]=1762,["Enemy_Flag"]=16,["Enemy_ID"]=23,["Enemy_MovingDir"]=1343,["Enemy_PageLoc"]=93,["Enemy_State"]=31,["Enemy_X_Position"]=118,["Enemy_X_Speed"]=71,["Enemy_Y_Position"]=190,["Enemy_Y_Speed"]=143,["GameEngineSubroutine"]=15,["GuestPowerupActive"]=27645,["LevelNumber"]=1889,["NumberofLives"]=1887,["OperMode"]=1905,["PlayerStatus"]=1883,["Player_PageLoc"]=92,["Player_State"]=30,["Player_X_Position"]=117,["Player_Y_HighPos"]=164,["Player_Y_Position"]=189,["SavedJoypadBits"]=220,["ScreenLeft_PageLoc"]=1821,["ScreenLeft_X_Pos"]=1823,["SelectedCharacter"]=24578,["WorldNumber"]=1892}
local ROUTE_ATTR={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,65,65,65,65,65,65,65,65,65,65,65,65,65,65,65,65,69,69,69,69,69,69,69,69,69,69,69,69,71,69,69,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,128,128,128,128,128,128,128,133,133,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,193,193,193,193,197,197,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
local routePoints={{["name"]="BbOriginal_D36B",["pc"]=42056,["offset"]=25672,["data"]="bd01c029"},{["name"]="BbNativeProxyCaptureCommit",["pc"]=47258,["offset"]=30874,["data"]="3860a200"},{["name"]="EnemyStomped",["pc"]=38918,["offset"]=1038342,["data"]="b517c912"}}
L.PowerUpType=52
L.BoundingBox_UL_Corner=1624
L.EnemyBoundingBoxCoord=1628
L.Player1ScoreDisplay=1967
L.FloateyNum_Control=269
L.FloateyNum_Timer=297
L.Square2SoundQueue=260
L.GuestPowerupAge=27646
L.GuestPowerupActive=27645
local Q={launch={bob=identity}}
local BUB_NATIVE_OBSERVER_CONFIG={ram=L,hooks={}}
local age,settled,settledLast=0,0,-1
local function ram(at)return read(at)end
local function shot()end
local counts={captures=0,pops=0,launches=0,source_bubble_ride_restarts=0,source_total_jump_starts=0,native_enemy_stomps=0}
local tokens,pool={},{}
local function sampleBubble()
 for i=0,14 do local on=work(2,0x88+4*i)~=0;if on and not pool[i]then counts.launches=counts.launches+1 end;pool[i]=on end
 for i=0,5 do
  local at=0x320+16*i;local on=work(2,at)~=0
  if not on and tokens[i]then
   if read(L.Enemy_ID+i)==tokens[i] and read(L.Enemy_State+i)&32~=0 then counts.pops=counts.pops+1 end
   tokens[i]=nil
  end
 end
end
local BUB_OBSERVER={}
function BUB_OBSERVER.summary()local q={passed=true,failures=0,completed_Main=updates};for k,v in pairs(counts)do q[k]=v end;return q end
BUB_OBSERVER.finish=BUB_OBSERVER.summary
for _,h in ipairs(routePoints)do
 if h.name=='BbOriginal_D36B'then
  local bytes={};for k=1,#h.data,2 do bytes[#bytes+1]=tonumber(h.data:sub(k,k+1),16)end
  BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B={pc=h.pc,physical=h.offset,bytes=bytes}
 end
 emu.addMemoryCallback(guard(function()
  if not game or not active()then return end
  local kind=h.name=='EnemyStomped'and emu.memType.nesPrgRom or emu.memType.nesWorkRam
  if not mapped(h.pc,kind,h.offset)then return end
  for k=1,#h.data,2 do assert(read(h.pc+(k-1)//2)==tonumber(h.data:sub(k,k+1),16),'Actual trap/jump/native contact entry')end
  local x=emu.getState()['cpu.x']
  if h.name=='BbOriginal_D36B'then
   counts.source_total_jump_starts=counts.source_total_jump_starts+1
   if work(2,x+9)~=0 and work(2,x+1)&128~=0 then counts.source_bubble_ride_restarts=counts.source_bubble_ride_restarts+1 end
  elseif h.name=='BbNativeProxyCaptureCommit'then
   assert(x<6 and work(2,0x320+16*x)~=0,'Real source capture commit')
   counts.captures=counts.captures+1;tokens[x]=work(2,0x321+16*x)
  else counts.native_enemy_stomps=counts.native_enemy_stomps+1 end
 end),emu.callbackType.exec,h.pc)
end
local obstacles={
 {kind='pipe',left=448,right=480,top=176,lead=96},
 {kind='pipe',left=608,right=640,top=160,lead=96},
 {kind='pipe',left=736,right=768,top=144,lead=96},
 {kind='pipe',left=912,right=944,top=144,lead=96},
 {kind='pit',left=1104,right=1136,lead=72},
 {kind='pit',left=1376,right=1424,lead=56},
 {kind='pit',left=2448,right=2480,lead=72}}
local full_part,full_index,full_step,full_last='approach',1,0,0
local full_lives,full_base,full_ride_base,full_start_y,full_min_y=nil,nil,nil,nil,255
local full_events,full_clears={},{}
local full_pad,full_max_x,full_last_x,full_stationary={},0,nil,0
local full_combat,full_attack_step,full_attack_base=nil,0,nil
local full_combat_focus,full_combat_cooling=false,false
local full_combat_waiting_height=false
local full_ground_pulse,full_last_engine,full_near_castle=0,8,false
local full_normal_takeoff=nil
local full_normal_actual={}
local full_edge_decisions,full_edge_dropped,full_edge_row={},0,nil
local full_stair_actual,full_stair_landings,full_stair_controls={},{},{}
local full_stair_target,full_stair_y,full_stair_base,full_stair_seen=nil,nil,nil,false
local full_stair_resume='approach'
local full_csv=nil
local function full_state(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function full_x(i)
 if i then return ram(L.Enemy_X_Position+i)+256*ram(L.Enemy_PageLoc+i)end
 return r('Player_X_Position')+256*r('Player_PageLoc')
end
local function full_solid(x,y)
 if y<32 or y>=240 then return false,-1 end
 local at=L.Block_Buffer_1+((x//256)&1)*208+((y-32)//16)*16+(x%256)//16
 local tile=ram(at);return ROUTE_ATTR[tile+1]&3==1,tile
end

local function full_contact_sample()end
local full_rearm_target,full_rearm_clock,full_rearm_age=nil,nil,0
local full_rearm_mode,full_rearm_rows,full_rearm_dropped='rewind',{},0
local function full_runup(obstacle)
 local target=obstacle.left-obstacle.lead
 local prior=obstacles[full_index-1]
 -- Native left collision stops at643 beside the prior pipe ending640.
 if prior and prior.kind=='pipe'then target=math.max(target,prior.right+4)end
 return target
end
local function full_launch_ready(actor)
 local oy=Q.launch.bob==1 and 8 or 0
 return full_state(actor+8)==0 and full_state(0x301)&64==0
  and full_state(0x102+oy)&64~=0
end

local function full_support_probe()
 local x,y=full_x(),r('Player_Y_Position');local samples={}
 for _,dx in ipairs({0,1,7,14,15})do
  local solid,tile=full_solid(x+dx,y+32)
  local at=L.Block_Buffer_1+(((x+dx)//256)&1)*208+((y+32-32)//16)*16+((x+dx)%256)//16
  samples[#samples+1]={dx=dx,x=x+dx,y=y+32,tile=tile,
   attribute=tile>=0 and ROUTE_ATTR[tile+1]or-1,solid=solid,buffer_address=at}
 end
 local actor=Q.launch.bob==1 and 0x42 or 0x2e
 return{Main=BUB_OBSERVER.summary().completed_Main,x=x,y=y,
  native_state=r('Player_State'),native_Y_speed=ram(142),
  native_Y_high=ram(BUB_NATIVE_OBSERVER_CONFIG.ram.Player_Y_HighPos),
  source_selector=full_state(actor+3),source_clock=full_state(0x1f),
  source_x=full_state(0x103+(Q.launch.bob==1 and 8 or 0)),
  source_y=full_state(0x100+(Q.launch.bob==1 and 8 or 0)),
  camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos'),foot=samples}
end


local function full_normal_jump_ready(actor)
 -- NativeState0/DY0 and a real native foot are mandatory. The approved
 -- landing adapter clears healthy source2/3 by original D41C before the
 -- PlayerStep that consumes this fresh A. Injury/ascent remain excluded.
 local selector=full_state(actor+3)
 if selector~=0 and selector~=2 and selector~=3 then return false end
 if r('Player_State')~=0 or ram(142)~=0
  or ram(BUB_NATIVE_OBSERVER_CONFIG.ram.Player_Y_HighPos)~=1 then return false end
 local s=full_support_probe()
 return s.foot[2].solid or s.foot[4].solid
end

do
 local h=BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B
 emu.addMemoryCallback(function()
  if phase~='fullstage'or(full_part~='normal-pit'and full_part~='stair-air')then return end
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.physical then return end
  for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Actual original normal jump entry')end
  local target=full_part=='stair-air'and full_stair_actual or full_normal_actual
  local cap=full_part=='stair-air'and 8 or 2
  assert(#target<cap,'Bounded actual original supported stair/pit jumps')
  local q=full_support_probe();local actor=Q.launch.bob==1 and 0x42 or 0x2e
  assert(q.native_state==0 and(q.foot[2].solid or q.foot[4].solid),'Actual original final-pit jump has native left or right foot support')
  assert(full_state(actor+9)==0 and full_state(actor+1)&128~=0,'Original normal jump has genuine A and no bubble support marker')
  q.original_PC=h.pc;q.Main_pending=BUB_OBSERVER.summary().completed_Main+1
  q.route_section=full_index==8 and'castle-stairs'or'pre-pit-stairs'
  q.source_held=full_state(actor+1);q.support_marker=full_state(actor+9)
  target[#target+1]=q
 end,emu.callbackType.exec,h.pc)
end

local function full_rearm_has_support(actor)
 if r('Player_State')==0 then return true end
 local x,y=full_x(),r('Player_Y_Position')
 -- Native collision initializes state2 before its consumers. The actual
 -- negative retained floor contact, zeroYspeed and original selector0.
 if ram(BUB_NATIVE_OBSERVER_CONFIG.ram.Player_Y_HighPos)~=1
  or ram(142)~=0 or full_state(actor+3)~=0 or y&15~=0 then return false end
 local left=full_solid(x+1,y+32);local right=full_solid(x+14,y+32)
 return left and right
end

local function full_rearm_sample(actor)
 if#full_rearm_rows>=192 then full_rearm_dropped=full_rearm_dropped+1;return end
 local oy=Q.launch.bob==1 and 8 or 0
 full_rearm_rows[#full_rearm_rows+1]={Main=BUB_OBSERVER.summary().completed_Main,
  x=full_x(),target=full_rearm_target,mode=full_rearm_mode,
  source_clock=full_state(0x1f),cooldown=full_state(actor+8),
  previous_source_held=full_state(0x301),native_held=r('SavedJoypadBits'),
  source_facing=full_state(0x102+oy),facing_source_updates=full_rearm_age,
  support_probe=full_support_probe()}
end


local function full_enemy_snapshot()
 local rows={}
 for slot=0,5 do rows[#rows+1]={slot=slot,flag=ram(L.Enemy_Flag+slot),
  ID=ram(L.Enemy_ID+slot),state=ram(L.Enemy_State+slot),
  x=full_x(slot),y=ram(L.Enemy_Y_Position+slot),
  speed=ram(L.Enemy_X_Speed+slot),direction=ram(L.Enemy_MovingDir+slot),
  token=full_state(0x320+16*slot),source_selector=full_state(0x68+4*slot+3),
  source_x=full_state(0x113+8*slot),source_y=full_state(0x110+8*slot)}end
 return rows
end

local function full_event(kind)
 assert(#full_events<96,'Bounded fullstage route events')
 if kind:match('^freshB%-close%d+%-natural%-enemy$')then full_contact_sample(kind,false)end
 local q=BUB_OBSERVER.summary();local actor=Q.launch.bob==1 and 0x42 or 0x2e
 full_events[#full_events+1]={kind=kind,Main=q.completed_Main,index=full_index,
  x=full_x(),y=r('Player_Y_Position'),part=full_part,selector=full_state(actor+3),
  cooldown=full_state(actor+8),previous_source_held=full_state(0x301),
  support=full_state(actor+9),clock=full_state(0x1f),rides=q.source_bubble_ride_restarts,
  native_stomps=q.native_enemy_stomps,captures=q.captures,pops=q.pops}
end
local function full_write(ok,why,q)
 routeResult={passed=ok,reason=why,clears=full_clears,pops=q.pops,captures=q.captures,
 launches=q.launches,rides=q.source_bubble_ride_restarts,jumps=q.source_total_jump_starts,
 current_x=full_x(),current_y=r('Player_Y_Position'),part=full_part,index=full_index,
 world=r('WorldNumber'),level=r('LevelNumber'),engine=r('GameEngineSubroutine'),
 helpers_added=false,initial_lives=full_lives,final_lives=r('NumberofLives')}
end
local function full_fail(why)local q=BUB_OBSERVER.finish();full_write(false,why,q);assert(false,why)end
local function full_label()return phase=='fullstage'and full_part or phase end
local function full_keys()local keys={}for k,v in pairs(full_pad)do if v then keys[#keys+1]=k end end;return keys end
local function full_begin()
 phase='fullstage';age=0;full_lives=r('NumberofLives');full_base=BUB_OBSERVER.summary()
 full_last=full_base.completed_Main
 full_pad={right=true};full_event('actual-cold-start');shot('full11-cold-spawn')
end
local function full_target()
 local best,gap=nil,10000
 for i=0,5 do
  local flag=ram(L.Enemy_Flag+i);local id=ram(L.Enemy_ID+i);local dx=full_x(i)-full_x()
  if flag>0 and flag<128 and(id==6 or id==0)and ram(L.Enemy_State+i)&32==0 and dx>0 and dx<gap and math.abs(ram(L.Enemy_Y_Position+i)-r('Player_Y_Position'))<=32 then best,gap=i,dx end
 end
 return best,gap
end


local actualMoves=0;local currentPickup=nil
local function itemScore()local value=0;for i=0,5 do value=value*10+read(Stock.ram.Player1ScoreDisplay+i)end;return value end
local function itemBox(at)local t={};for i=0,3 do t[#t+1]=read(at+i)end;return t end
local function itemState()local q=state();q.moves=actualMoves;q.score=itemScore();q.flags=work(2,(identity==1 and 0x42 or 0x2e)+2);q.power=r('PlayerStatus');return q end
local function regularItem(slot)
 return slot>=0 and slot<6 and read(L.Enemy_Flag+slot)==1 and read(L.Enemy_ID+slot)==46
  and read(L.Enemy_State+slot)>=128 and read(L.PowerUpType+slot)<2
end
local function pickupRecord(slot)
 local kind=read(L.PowerUpType+slot);flower.pickups=flower.pickups or{}
 local key=kind==0 and'M'or'F';flower.pickups[key]=flower.pickups[key]or{kind=kind,slot=slot,freeze=0}
 return flower.pickups[key]
end
for name,h in pairs(Stock.hooks)do
 emu.addMemoryCallback(guard(function()
  if not game or r('SelectedCharacter')~=39 then return end
  local kind=h.kind==1 and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not mapped(h.pc,kind,h.offset)then return end
  for i=1,#h.data,2 do assert(read(h.pc+(i-1)//2)==tonumber(h.data:sub(i,i+1),16),'Exact current mature pickup/move/animation hook '..name)end
  local cpu=emu.getState();local slot=cpu['cpu.x']
  if name=='BbNativeUpdate'then if active()then actualMoves=actualMoves+1 end
  elseif name=='BbNativePickup'and regularItem(slot)then
   local p=pickupRecord(slot);assert(not p.collector,'One physical regular collector per kind')
   p.collector={state=itemState(),slot=slot,x=full_x(slot),y=read(L.Enemy_Y_Position+slot),
    player_box=itemBox(Stock.ram.BoundingBox_UL_Corner),item_box=itemBox(Stock.ram.EnemyBoundingBoxCoord+slot*4)}
   currentPickup=p
  elseif name=='BbGrantAfter'and currentPickup then
   local p=currentPickup;p.grant={state=itemState(),source_actor=slot}
   assert(slot==(identity==1 and 0x42 or 0x2e),'Actual selected original source actor')
   assert(p.grant.state.flags==(p.kind==0 and 1 or 7),'Original item4/item2 masks applied by actual code')
  elseif name=='SetupFloateyNumber'and(regularItem(slot)or(currentPickup and currentPickup.slot==slot))then
   -- Actual MarioSourcePowerupCollision erases the actor before this call.
   -- Keep the authenticated collector/slot token through native bookkeeping.
   local p=currentPickup and currentPickup.slot==slot and currentPickup or pickupRecord(slot)
   p.setup={control=cpu['cpu.a'],state=itemState()}
  elseif name=='EraseEnemyObject'and currentPickup and currentPickup.slot==slot then
   currentPickup.erase=itemState()
  elseif name=='GuestPowerupUpdate'and currentPickup and r('GuestPowerupActive')==1 then
   currentPickup.freeze=currentPickup.freeze+1
   currentPickup.first_age=currentPickup.first_age or read(Stock.ram.GuestPowerupAge)
   currentPickup.last_age=read(Stock.ram.GuestPowerupAge)
  end
 end),emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(guard(function(at,value)
 if currentPickup and not currentPickup.cue and value==32 then
  currentPickup.cue={value=value,state=itemState(),PC=emu.getState()['cpu.pc']}
 end
end),emu.callbackType.write,Stock.ram.Square2SoundQueue)
local function observePickup()
 if currentPickup then
  local p=currentPickup;local control=read(Stock.ram.FloateyNum_Control+p.slot)
  if control==6 then p.popup=p.popup or{control=control,timer=read(Stock.ram.FloateyNum_Timer+p.slot),state=itemState()}end
 end
end
local function requirePickup(p,post)
 assert(p and p.collector and p.grant and p.erase and p.setup and p.popup and p.cue,'Actual physical collector/grant/erase/popup/cue witnesses')
 assert(p.setup.control==6 and p.popup.control==6 and p.cue.value==32,'Native1000 popup and cue32')
 assert(p.freeze==60,'Exactly60 actual hosted powerup updates')
 assert(actualMoves-p.grant.state.moves>=post,'Actual Bub movement calls after source grant')
 assert(itemScore()==p.collector.state.score+1000,'Actual delayed1000 score')
end

local poweredGeneration,poweredSlot=nil,nil
local function poweredSample(slot)
 local oy=identity==1 and 8 or 0;local bo=0x188+8*slot
 return {slot=slot,kind=full_state(0x88+4*slot),
  dx=((full_state(bo+3)-full_state(0x103+oy)+128)%256)-128,
  dy=((full_state(bo)-full_state(0x100+oy)+128)%256)-128}
end
local function poweredGrowth(q,base,step)
 if poweredGeneration~=base.completed_Main then poweredGeneration=base.completed_Main;poweredSlot=nil end
 if q.launches>base.launches and poweredSlot==nil then
  local best=nil
  for i=0,14 do local s=poweredSample(i)
   if(s.kind==1 or s.kind==2)and s.dx>=0 and s.dx<96 and(not best or math.abs(s.dx-34)<math.abs(best.dx-34))then best=s end
  end
  if best then poweredSlot=best.slot end
 end
 local pad={right=step<4,b=step<4};local s=poweredSlot and poweredSample(poweredSlot)or nil
 if s and step>=4 then pad.right=s.dx>34 end
 local actor=identity==1 and 0x42 or 0x2e
 if s and s.kind==2 and s.dx>=30 and s.dx<=36 and s.dy>=-20 and s.dy<=-16
  and full_normal_jump_ready(actor)and full_state(0x301)&128==0 then
  local row={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),bubble=s,support=full_support_probe()}
  assert(#flower.takeoffs<8,'Bounded actual powered bubble takeoffs');flower.takeoffs[#flower.takeoffs+1]=row
  return{right=true,a=true},true
 end
 if q.completed_Main%8==0 then
  local t=flower.growth;t[#t+1]={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),step=step,bubble=s,selector=full_state(actor+3),held=full_state(0x301)}
  if#t>24 then table.remove(t,9)end
 end
 return pad,false
end

local groundRearm=nil
local function poweredGround(q)
 if not groundRearm or groundRearm.generation~=full_ride_base.completed_Main then
  groundRearm={generation=full_ride_base.completed_Main,release=sourceUpdates,jumps=q.source_total_jump_starts}
 end
 local g=groundRearm
 if g.press and q.source_total_jump_starts>g.jumps then
  flower.rearm_admissions=flower.rearm_admissions+1;groundRearm=nil
  return{right=true,a=true}
 end
 if not g.press then
  if sourceUpdates-g.release>=2 and full_state(0x301)&128==0 then
   g.press=sourceUpdates;flower.rearm_requests=flower.rearm_requests+1
   assert(flower.rearm_requests<24,'Bounded genuine supported retry requests')
  else return{right=true}end
 end
 assert(sourceUpdates-g.press<12,'Supported fresh A must reach actual original jump entry')
 return{right=true,a=true}
end

local function poweredAir(q,base)
 if q.source_bubble_ride_restarts>base.source_bubble_ride_restarts then return nil end
 local best=nil
 for i=0,14 do local s=poweredSample(i)
  if s.kind==2 and s.dx>-40 and s.dx<48 and(not best or math.abs(s.dx-8)<math.abs(best.dx-8))then best=s end
 end
 if best then
  local t=flower.align_trace or{};flower.align_trace=t
  t[#t+1]={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),bubble=best,held=full_state(0x301),cached_direction=full_state((identity==1 and 0x42 or 0x2e)+5)}
  if#t>24 then table.remove(t,9)end
  -- Actual D36B copies held&3 into the original jump-direction latch.
  -- Neutral horizontal alignment avoids a new Left-facing support bounce;
  -- when the real bubble approaches the feet, keep its restart rightward.
  return{right=best.dx>12 or best.dy>=8,a=true}
 end
end


local closeFight=nil
local function closeRect(slot)
 local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
 local wx=slot==nil and full_x()or full_x(slot)
 local rel=(wx-camera)&255
 local at=slot==nil and Stock.ram.BoundingBox_UL_Corner or Stock.ram.EnemyBoundingBoxCoord+4*slot
 local a={};for i=0,3 do a[#a+1]=read(at+i)end
 a[1]=wx+((a[1]-rel+128)%256)-128;a[3]=wx+((a[3]-rel+128)%256)-128
 return a
end
local function closeThreat(q,actor,x,y,grounded)
 if x<600 or x>=720 or(full_index~=2 and full_index~=3)then return false end
 if full_part~='approach'and full_part~='jump'and full_part~='cross'then return false end
 local target=nil
 for i=0,5 do
  local flag=read(L.Enemy_Flag+i);local id=read(L.Enemy_ID+i)
  local dx=full_x(i)-x;local ey=read(L.Enemy_Y_Position+i)
  if flag>0 and flag<128 and(id==6 or id==0)and read(L.Enemy_State+i)&32==0
   and dx>0 and dx<=80 and math.abs(ey-y)<=48 and(not target or dx<target.dx)then
   target={slot=i,id=id,flag=flag,state=read(L.Enemy_State+i),dx=dx,x=full_x(i),y=ey,direction=read(L.Enemy_MovingDir+i),box=closeRect(i)}
  end
 end
 local body=closeRect(nil)
 if target and q.completed_Main~=flower.closeLast then
  flower.closeLast=q.completed_Main;flower.close_rows=flower.close_rows or{}
  local t=flower.close_rows;t[#t+1]={Main=q.completed_Main,x=x,y=y,native=r('Player_State'),selector=full_state(actor+3),part=full_part,index=full_index,
   held=full_state(0x301),saved=r('SavedJoypadBits'),body=body,target=target,cooldown=full_state(actor+8),pad=pad}
  if#t>20 then table.remove(t,6)end
 end
 if closeFight then
  local c=closeFight;local age=q.completed_Main-c.Main
  if q.captures>c.captures and q.pops>c.pops then
   flower.close_retired=flower.close_retired or{}
   flower.close_retired[#flower.close_retired+1]={Main=q.completed_Main,x=x,y=y,slot=c.slot,captures=q.captures-c.captures,pops=q.pops-c.pops}
   closeFight=nil;full_pad={};return true
  end
  assert(age<60,'Actual close-defence shot must trap and pop the threat')
  -- Stay clear while the projectile catches the real actor; approach only
  -- after actual source capture makes contact safe and needed for the pop.
  full_pad={right=q.captures>c.captures,b=age<4};return true
 end
 if not target or target.dx>48 then return false end
 local disjoint=body[3]<target.box[1]or body[1]>target.box[3]or body[4]<target.box[2]or body[2]>target.box[4]
 assert(disjoint,'Close-defence begins while actual native body/enemy boxes are disjoint')
 local aligned=math.abs(target.y-(y+8))<=8
 local ready=full_state(actor+8)==0 and full_state(0x301)&64==0
 local right=full_state(0x102+(identity==1 and 8 or 0))&64~=0
 if grounded and full_normal_jump_ready(actor)and aligned and ready and target.dx>=16 and target.dx<=40 and(right or target.dx>=20)then
  if not right then full_pad={right=true};return true end
  closeFight={Main=q.completed_Main,slot=target.slot,captures=q.captures,pops=q.pops}
  flower.close_shots=flower.close_shots or{}
  flower.close_shots[#flower.close_shots+1]={Main=q.completed_Main,x=x,y=y,body=body,target=target,held=full_state(0x301),cooldown=full_state(actor+8)}
  full_pad={b=true};return true
 end
 -- Below the second-pipe lip the landing floor is real. Retire Right/A
 -- before touchdown and retreat while preserving a real safe landing foot.
 local safe=full_solid(x-8,208)and full_solid(x+7,208)
 full_pad={left=safe};return true
end

local function full_tick_base(finish)
 local q=BUB_OBSERVER.summary();local engine=r('GameEngineSubroutine')
 if r('NumberofLives')~=full_lives then full_fail('Fullstage route lost a life')end
 if r('WorldNumber')==0 and r('LevelNumber')==1 then
  full_pad={}
  if engine==8 and r('Player_Y_Position')==176 and r('Player_State')==0 then
   if q.completed_Main~=settledLast then settledLast=q.completed_Main;settled=settled+1 end
  else settled=0 end
  if settled>=25 then
   assert(#full_clears==7,'All four pipes and three pits recorded')
   assert(q.pops>0 and q.captures>0 and q.source_bubble_ride_restarts>=6,'Actual natural source trap/pop and earned bubble support')
   full_write(true,'Full nonshortcut 1-1 and 25 living grounded 1-2 Main',q);finish(true,routeResult.reason)
  end
  return
 end
 if r('SelectedCharacter')~=39 or r('OperMode')~=1 then full_fail('Fullstage route lost its actual owner')end
 if engine==11 then full_fail('Fullstage natural death')end
 if engine~=full_last_engine then full_event('native-engine-transition');full_last_engine=engine end
 if engine~=8 then full_pad={right=true};return end
 if q.completed_Main==full_last then return end
 assert(q.completed_Main==full_last+1,'Actual completed fullstage Main cadence')
 full_last=q.completed_Main;full_step=full_step+1
 if q.completed_Main-full_base.completed_Main>10000 then full_fail('Bounded10000Main fullstage route')end
 local x,y=full_x(),r('Player_Y_Position');local grounded=r('Player_State')==0
 full_max_x=math.max(full_max_x,x)
 if full_last_x==x then full_stationary=full_stationary+1 else full_stationary=0;full_last_x=x end
 if full_stationary>500 then full_fail('Source route stationary500Main without a completed crossing')end
 local actor=Q.launch.bob==1 and 0x42 or 0x2e
 if full_state(actor+3)&128~=0 or full_state(0x307)~=0 then full_fail('Fullstage source injury/death')end
 if closeThreat(q,actor,x,y,grounded)then return end
 full_edge_row=nil
 if full_index==7 and x>=2436 and x<=2448 then
  if#full_edge_decisions<48 then
   local side,side_tile=full_solid(x+20,y+31)
   local forward,edge_tile=full_solid(x+5,y+32)
   full_edge_row={Main=q.completed_Main,part=full_part,support=full_support_probe(),
    side=side,side_tile=side_tile,edge_missing=not forward,edge_tile=edge_tile,edge_probe_dx=5,
    jump_ready=full_normal_jump_ready(actor),previous_source_held=full_state(0x301),
    source_held=full_state(actor+1),source_cooldown=full_state(actor+8),
    prior_pad=r('SavedJoypadBits'),combat=full_combat}
   full_edge_decisions[#full_edge_decisions+1]=full_edge_row
  else full_edge_dropped=full_edge_dropped+1 end
 end
 if x>3000 and not full_near_castle then full_near_castle=true;full_event('near-native-castle');shot('near-castle')end
 if full_part=='grow'and q.captures>full_ride_base.captures then
  full_part='clear-route';full_step=0;full_pad={}
  full_event('route-bubble-intercepted-by-natural-enemy')
  full_events[#full_events].actual_enemies=full_enemy_snapshot()
 end
 if full_part=='clear-route'then
  if not full_rearm_has_support(actor)then full_fail('Intercepted route cleanup lost actual floor support')end
  if full_step>240 then full_fail('Bounded intercepted route bubble recovery')end
  local trapped=false
  for slot=0,5 do if full_state(0x320+16*slot)~=0 then trapped=true end end
  if trapped and not full_combat then
   -- Original trap clock39 is allowed to complete. Release both buttons;
   -- retreat only over the native body foot's verified solid terrain.
   local target=full_runup(obstacles[full_index])
   local behind=full_solid(x-2,y+32);local inside=full_solid(x+11,y+32)
   full_pad=x>target+1 and behind and inside and{left=true}or{}
   return
  end
 end
 if full_combat then
  full_contact_sample('completed-combat-Main',false)
  full_attack_step=full_attack_step+1;full_pad={right=true,b=full_attack_step<4}
  if q.pops>full_attack_base.pops or ram(L.Enemy_State+full_combat)&32~=0 or ram(L.Enemy_Flag+full_combat)==0 then
   full_event('natural-native-enemy-defeat');full_combat=nil;full_attack_step=0;full_combat_focus=false;full_combat_cooling=false
  elseif full_attack_step>45 then full_fail('Close source-proven shot failed to defeat natural enemy')end
  return
 end
 if(full_part=='approach'or full_part=='march'or full_part=='clear-route')and(grounded or full_rearm_has_support(actor))then
  local enemy,gap=full_target()
  if not enemy then full_combat_focus=false;full_combat_cooling=false end
  if enemy and(gap<=48 or full_combat_focus)then
   full_combat_focus=true
   if ram(L.Enemy_Y_Position+enemy)~=y+8 or ram(L.Enemy_Y_Speed+enemy)~=0 then
    local behind=full_solid(x-2,y+32);local inside=full_solid(x+11,y+32)
    full_pad=behind and inside and{left=true}or{}
    if not full_combat_waiting_height then
     full_combat_waiting_height=true;full_event('falling-target-release-retreat-before-ground-shot')
     full_events[#full_events].target={slot=enemy,gap=gap,y=ram(L.Enemy_Y_Position+enemy),speed=ram(L.Enemy_Y_Speed+enemy)}
    end
    return
   end
   if full_combat_waiting_height then
    full_combat_waiting_height=false;full_event('natural-target-source-ground-height-aligned')
    full_events[#full_events].target={slot=enemy,gap=gap,y=ram(L.Enemy_Y_Position+enemy),speed=ram(L.Enemy_Y_Speed+enemy)}
   end
   if full_state(actor+8)~=0 or full_state(0x301)&64~=0 then
    -- Real cooldown is25updates. Retreat only onto actual floor; at an
    -- authored ledge releaseB and wait without stepping back into the pit.
    local behind=full_solid(x-2,y+32);local inside=full_solid(x+11,y+32)
    full_pad=behind and inside and{left=true}or{}
    if not full_combat_cooling then
     full_combat_cooling=true;full_event('original-shot-cooldown-release-retreat')
    end
    return
   end
   if full_combat_cooling then
    full_combat_cooling=false;full_event('original-combat-cooldown-zero-B-released')
   end
   local oy=Q.launch.bob==1 and 8 or 0
   full_pad={right=true}
   if full_state(0x102+oy)&64==0 then return end
   local fire_gap=ram(L.Enemy_MovingDir+enemy)==1 and 20 or 24
   if gap<=fire_gap then
    if gap<16 then full_fail('Enemy reached unsafe distance before close source shot')end
    full_combat=enemy;full_attack_step=0;full_attack_base=q;full_pad.b=true;full_event('freshB-close'..fire_gap..'-natural-enemy')
   end
   return
  end
 end
 local obstacle=obstacles[full_index]
 if not obstacle and full_part=='approach'then full_part='march' end
 if full_part=='approach'then
  full_pad={right=true}
  if full_index==7 and x>=2330 then
   if grounded then
    local side=full_solid(x+20,y+31)
    local edge=not full_solid(x+5,y+32)
    if side and(full_state(actor+3)==0 or full_state(actor+3)==3)then
     assert(#full_stair_controls<8,'Bounded genuine staircase retreats')
     full_stair_target=x-6;full_part='stair-back';full_step=0;full_pad={left=true}
     full_stair_controls[#full_stair_controls+1]={Main=q.completed_Main,x=x,y=y,target=full_stair_target,support=full_support_probe()}
    elseif edge and x>=2432 and x<2448 and full_normal_jump_ready(actor)then
     full_normal_takeoff=full_support_probe()
     if not full_normal_takeoff.foot[2].solid then full_fail('Final pit normal takeoff lacks real left-foot support')end
     full_part='normal-pit';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
     full_ground_pulse=1;full_pad={right=true,a=true}
     full_event('original-normal-jump-from-supported-final-stair')
     full_events[#full_events].actual_takeoff=full_normal_takeoff
    end
   end
   return
  end
  if grounded and x<obstacle.left-obstacle.lead-32 then
   local need=not full_solid(x+12,y+32)or full_solid(x+20,y+31)
   if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then
    full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3
   else full_ground_pulse=0 end
  else full_ground_pulse=0 end
  if grounded and x>=obstacle.left-obstacle.lead then
   local target=full_runup(obstacle)
   if x>target+2 or not full_launch_ready(actor)then
    full_part='rearm';full_step=0;full_rearm_target=target
    full_rearm_clock=full_state(0x1f);full_rearm_age=0;full_rearm_mode='rewind'
    full_pad=x>target and{left=true}or{right=true}
    full_event('source-shot-rearm-begin');full_rearm_sample(actor)
   else
    full_part='grow';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
    full_pad={right=true,b=true};full_event('original-free-bubble-launch-for-'..obstacle.kind)
   end
  end
 elseif full_part=='rearm'then
  if not full_rearm_has_support(actor)then full_rearm_sample(actor);full_fail('Native runup rearm lost genuine support')end
  if full_step>150 then full_fail('Bounded source shot rearm')end
  if full_rearm_mode=='rewind'and x>full_rearm_target+1 then
   full_pad={left=true}
  else
   if full_rearm_mode=='rewind'then
    full_rearm_mode='face-right';full_rearm_age=0;full_rearm_clock=full_state(0x1f)
   else
    local now=full_state(0x1f);local elapsed=(now-full_rearm_clock)&255
    if elapsed>4 then full_fail('Unexpected source clock gap during rearm')end
    full_rearm_age=full_rearm_age+elapsed;full_rearm_clock=now
   end
   local oy=Q.launch.bob==1 and 8 or 0
   if full_rearm_age<1 or full_state(0x102+oy)&64==0 then
    full_pad={right=true}
   else
    full_pad={}
    if full_launch_ready(actor)then
     full_event('source-cooldown-zero-B-released-right-facing')
     full_part='grow';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
     full_pad={right=true,b=true};full_event('original-free-bubble-launch-for-'..obstacle.kind)
    end
   end
  end
  full_rearm_sample(actor)
 elseif full_part=='stair-back'then
  local support=full_support_probe()
  if not grounded or not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original staircase retreat lost actual native foot support')end
  if full_step>20 then full_fail('Bounded six-pixel source staircase retreat')end
  if x>full_stair_target then full_pad={left=true}
  else
   if full_state(0x301)&128~=0 then full_fail('Original stair jump A was not released during retreat')end
   full_part='stair-air';full_step=0;full_stair_y=y;full_stair_base=q.source_total_jump_starts;full_stair_seen=false
   full_pad={right=true,a=true}
  end
 elseif full_part=='stair-air'then
  full_pad={right=true,a=full_step<3}
  if not grounded or y<full_stair_y then full_stair_seen=true end
  if full_stair_seen and grounded then
   if q.source_total_jump_starts~=full_stair_base+1 then full_fail('Stair step requires one genuine original source jump')end
   local support=full_support_probe()
   if not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original stair jump missed real native supported landing')end
   assert(#full_stair_landings<8,'Bounded actual staircase landings')
   full_stair_landings[#full_stair_landings+1]=support
   full_part=full_stair_resume;full_step=0;full_pad={right=true}
  elseif full_step>150 then full_fail('Original staircase jump missed supported landing')end
 elseif full_part=='clear-route'then
  -- Keep a safe grounded position while a surviving natural enemy approaches
  -- the proven close-shot window. The existing combat code above owns its
  -- vertical alignment, original cooldown, fresh B, capture and actual defeat.
  full_pad={}
  local enemy=full_target()
  if not enemy then
   full_event('natural-enemy-corridor-cleared-rearm-original-ride')
   full_part='approach';full_step=0
  end
 elseif full_part=='grow'then
  local takeoff;full_pad,takeoff=poweredGrowth(q,full_ride_base,full_step)
  if full_step>=5 then assert(q.launches>full_ride_base.launches,'Real powered route bubble launch')end
  if takeoff then full_part='jump';full_step=0;full_event('actual-measured-powered-bubble-takeoff')end
  assert(full_step<180,'Measured source powered growth bound')
 elseif full_part=='jump'or full_part=='cross'then
  full_pad={right=true,a=true};full_min_y=math.min(full_min_y,y)
  if full_part=='jump'or full_part=='cross'then
   if not grounded then
    if groundRearm and groundRearm.press and q.source_total_jump_starts>groundRearm.jumps then
     flower.rearm_admissions=flower.rearm_admissions+1;groundRearm=nil
    end
    full_pad=poweredAir(q,full_ride_base)or full_pad
   elseif full_step>5 then
    full_pad=full_normal_jump_ready(actor)and poweredGround(q)or{right=true}
   end
  end
  if q.source_bubble_ride_restarts>full_ride_base.source_bubble_ride_restarts and full_part=='jump'then
   full_part='cross';full_event('earned-original-bubble-support-restart')
   if full_index==3 then shot('original-ride-third64px-pipe')end
  end
  if x>=obstacle.right+8 and grounded then
   if q.source_bubble_ride_restarts<=full_ride_base.source_bubble_ride_restarts then full_fail('Crossing missed required earned bubble support')end
   full_clears[#full_clears+1]={kind=obstacle.kind,left=obstacle.left,right_exclusive=obstacle.right,
    authored_top=obstacle.top,Main=q.completed_Main,x=x,y=y,minimum_anchor_y=full_min_y,
    original_support_restarts=q.source_bubble_ride_restarts-full_ride_base.source_bubble_ride_restarts}
   full_event('actual-supported-'..obstacle.kind..'-crossing');full_index=full_index+1
   full_part='approach';full_step=0;full_pad={right=true}
  elseif full_step>500 then full_fail('Original bubble crossing did not gain supported far side')end
 elseif full_part=='normal-pit'then
  full_pad={right=true};full_min_y=math.min(full_min_y,y)
  if grounded then
   local need=full_solid(x+20,y+31)or not full_solid(x+5,y+32)
   if need and full_normal_jump_ready(actor)then
    full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3
   else full_ground_pulse=0 end
  else full_ground_pulse=0 end
  if full_step>=5 and q.source_total_jump_starts<=full_ride_base.source_total_jump_starts then full_fail('Final pit missed genuine original normal jump')end
  if q.source_bubble_ride_restarts~=full_ride_base.source_bubble_ride_restarts or q.launches~=full_ride_base.launches then full_fail('Final pit normal jumps were unexpectedly bubble-assisted')end
  local starts=q.source_total_jump_starts-full_ride_base.source_total_jump_starts
  if starts>2 then full_fail('Final pit exceeded measured two original supported jumps')end
  if x>=obstacle.right+8 and grounded then
   if starts<1 or starts~=#full_normal_actual then full_fail('Final pit lacks actual source jump/support records')end
   full_clears[#full_clears+1]={kind=obstacle.kind,left=obstacle.left,right_exclusive=obstacle.right,
    Main=q.completed_Main,x=x,y=y,minimum_anchor_y=full_min_y,
    ability='original-normal43px-supported-jumps',actual_takeoffs=full_normal_actual,
    original_jump_starts=starts,original_support_restarts=0}
   full_event('actual-supported-final-pit-normal-jump-crossing')
   full_index=full_index+1;full_part='march';full_step=0;full_pad={right=true}
  elseif full_step>500 then full_fail('Original normal jumps failed final authored pit')end
 elseif full_part=='march'then
  full_pad={right=true}
  if grounded then
   local side=full_solid(x+20,y+31)
   if x>=2944 and x<3040 and side and(full_state(actor+3)==0 or full_state(actor+3)==3)then
    -- Exact native1-1 staircase, allremainingsteps source-CPU qualified.
    -- Earlierpipe/lowsteps retain oldcontrols; at the highsteps a genuine
    -- supported6pxLeft avoids the original D4BB air-direction clear.
    assert(#full_stair_controls<8,'Bounded genuine staircase retreats')
    full_stair_target=x-6;full_stair_resume='march';full_part='stair-back';full_step=0;full_pad={left=true}
    full_stair_controls[#full_stair_controls+1]={Main=q.completed_Main,x=x,y=y,target=full_stair_target,
     section='castle-stairs',support=full_support_probe()}
    full_event('original-supported-castle-stair-retreat')
   else
    local need=not full_solid(x+12,y+32)or side
    if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3 else full_ground_pulse=0 end
   end
  else full_ground_pulse=0 end
 end
end


local upgrade_phase,upgrade_age,upgrade_last='approach',0,-1
local upgrade_rows,upgrade_mature,upgrade_immature={},false,false
local upgrade_attempts=0
local function upgrade_item()
 for i=0,5 do
  if ram(L.Enemy_Flag+i)>0 and ram(L.Enemy_ID+i)==46 then
   return {slot=i,x=full_x(i),y=ram(L.Enemy_Y_Position+i),state=ram(L.Enemy_State+i)}
  end
 end
end
local function mushroom_tick(finish)
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local engine=r('GameEngineSubroutine')
 assert(r('NumberofLives')==2 and engine~=11,'Earned mushroom no death')
 if upgrade_phase=='approach' and x<310 then return full_tick_base(finish)end
 if upgrade_phase=='approach'then upgrade_phase='align';upgrade_age=0;full_pad={}end
 local item=upgrade_item();local flags=full_state((Q.launch.bob==1 and 0x42 or 0x2e)+2)
 if item then
  if item.state<128 then upgrade_immature=true;assert(flags&1==0,'Immature mushroom cannot upgrade source')else upgrade_mature=true end
 end
 if q.completed_Main~=upgrade_last then
  upgrade_last=q.completed_Main;upgrade_age=upgrade_age+1
  if #upgrade_rows<96 and (upgrade_age%8==0 or item)then upgrade_rows[#upgrade_rows+1]={Main=q.completed_Main,phase=upgrade_phase,x=x,y=y,item=item,flags=flags,engine=engine,status=r('PlayerStatus')}end
 end
 assert(upgrade_age<600,'Bounded earned first mushroom phase '..upgrade_phase)
 if engine==9 then full_pad={};return end
 if flags&1~=0 and r('GuestPowerupActive')==0 and engine==8 then
  assert(r('PlayerStatus')==1 and upgrade_immature and upgrade_mature,'Actual emerged/mature mushroom and completed native transformation')
  assert(q.captures>0 and q.pops>0,'First natural enemy genuinely trapped and popped')
  routeResult={passed=true,source_flags=flags,native_status=r('PlayerStatus'),
   observed_immature=upgrade_immature,observed_mature=upgrade_mature,
   bump_attempts=upgrade_attempts,captures=q.captures,pops=q.pops,rows=upgrade_rows}
  finish(true,'Natural first question-block mushroom and original bubble combat');return
 end
 if item then upgrade_phase='collect' end
 if upgrade_phase=='align'then
  full_pad={right=x<337,left=x>339}
  if x>=337 and x<=339 and r('Player_State')==0 and full_state(0x301)&128==0 then upgrade_attempts=upgrade_attempts+1;assert(upgrade_attempts<=3,'Bounded three natural mushroom bump attempts');upgrade_phase='bump';upgrade_age=0;full_pad={}end
 elseif upgrade_phase=='bump'then
  full_pad={a=upgrade_age<25}
  if upgrade_age>70 and r('Player_State')==0 then upgrade_phase='align';upgrade_age=0 end
 elseif upgrade_phase=='collect'then
  if item then full_pad={right=x<item.x-3,left=x>item.x+3}else full_pad={}end
 end
end


local function flowerPhase(p)flower.phase=p;flower.age=0;flower.phaseMain=updates end

local mountCombat=nil
local function mountDefence(q,actor,x,y)
 local enemies={};local nearest=nil
 for i=0,5 do
  local flag=read(L.Enemy_Flag+i);local id=read(L.Enemy_ID+i);local st=read(L.Enemy_State+i)
  if flag>0 and flag<128 and(id==6 or id==0)and st&32==0 then
   local a={slot=i,id=id,flag=flag,state=st,x=full_x(i),y=read(L.Enemy_Y_Position+i),direction=read(L.Enemy_MovingDir+i)}
   a.dx=a.x-x;enemies[#enemies+1]=a
   if math.abs(a.dx)<80 and math.abs(a.y-y)<=32 and(not nearest or math.abs(a.dx)<math.abs(nearest.dx))then nearest=a end
  end
 end
 if q.completed_Main~=flower.defenceLast then
  flower.defenceLast=q.completed_Main;flower.defence=flower.defence or{}
  local t=flower.defence
  if nearest or full_state(actor+3)&128~=0 then
   t[#t+1]={Main=q.completed_Main,x=x,y=y,selector=full_state(actor+3),enemies=enemies,pops=q.pops,captures=q.captures}
   if#t>20 then table.remove(t,7)end
  end
 end
 if mountCombat then
  local c=mountCombat;local age=q.completed_Main-c.Main
  if q.captures>c.captures and q.pops>c.pops then
   flower.retirements=flower.retirements or{}
   flower.retirements[#flower.retirements+1]={Main=q.completed_Main,x=x,y=y,target=c.target,captures=q.captures-c.captures,pops=q.pops-c.pops}
   mountCombat=nil;full_pad={};return true
  end
  assert(age<45,'Actual return-path bubble must trap/pop the real threat')
  full_pad={right=c.direction>0,left=c.direction<0,b=age<4};return true
 end
 if not nearest or not full_normal_jump_ready(actor)then return false end
 local dir=nearest.dx>=0 and 1 or-1;local gap=math.abs(nearest.dx)
 local function retreat()
  local safe=full_solid(x-dir*2,y+32)and full_solid(x+7,y+32)
  full_pad={right=safe and dir<0,left=safe and dir>0}
 end
 if math.abs(nearest.y-(y+8))>8 then retreat();return true end
 if full_state(actor+8)~=0 or full_state(0x301)&64~=0 then retreat();return true end
 local right=full_state(0x102+(identity==1 and 8 or 0))&64~=0
 if right~=(dir>0)then full_pad={right=dir>0,left=dir<0};return true end
 local away=nearest.direction==(dir>0 and 1 or 2);local fireGap=away and 20 or 24
 full_pad={right=dir>0,left=dir<0}
 if gap<=fireGap then
  assert(gap>=16,'Real threat stays outside body before fresh close shot')
  mountCombat={Main=q.completed_Main,direction=dir,target=nearest,captures=q.captures,pops=q.pops}
  full_pad.b=true
 end
 return true
end

local function full_tick(finish)
 observePickup()
 if flower.phase=='mushroom'then
  return mushroom_tick(function(ok,why)
   assert(ok,'Genuine frozen Mushroom prefix');flower.mushroom={source_flags=routeResult.source_flags,native_status=routeResult.native_status,
    observed_immature=routeResult.observed_immature,observed_mature=routeResult.observed_mature,
    captures=routeResult.captures,pops=routeResult.pops,bump_attempts=routeResult.bump_attempts};routeResult=nil
   flower.M_moves=sourceUpdates;flowerPhase('M-resume');full_pad={}
  end)
 end
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local engine=r('GameEngineSubroutine')
 local actor=identity==1 and 0x42 or 0x2e;local flags=full_state(actor+2);local item=upgrade_item()
 assert(r('NumberofLives')==2 and engine~=11,'Living natural Bub Flower continuation')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Flower continuation actual1-1')
 if q.completed_Main~=flower.last then
  flower.last=q.completed_Main;flower.age=flower.age+1
  if flower.phase=='travel'and(flower.last_jumps~=q.source_total_jump_starts or flower.last_rides~=q.source_bubble_ride_restarts or flower.last_ground~=r('Player_State'))then
   local t=flower.pipe_events;t[#t+1]={Main=q.completed_Main,x=x,y=y,part=full_part,native=r('Player_State'),selector=full_state(actor+3),cached_direction=full_state(actor+5),dy=ram(142),held=full_state(0x301),jumps=q.source_total_jump_starts,rides=q.source_bubble_ride_restarts,support=full_support_probe()}
   if#t>24 then table.remove(t,9)end
   flower.last_jumps=q.source_total_jump_starts;flower.last_rides=q.source_bubble_ride_restarts;flower.last_ground=r('Player_State')
  end
  if q.completed_Main%8==0 then
   local t=flower.trajectory;t[#t+1]={Main=q.completed_Main,phase=flower.phase,part=full_part,x=x,y=y,selector=full_state(actor+3),flags=flags,held=full_state(0x301),native=r('Player_State'),dy=ram(142),rides=q.source_bubble_ride_restarts,item=item}
   if#t>32 then table.remove(t,9)end
  end
 end
 assert(flower.age<1400,'Bounded real Flower phase '..flower.phase)
 if flower.phase=='M-resume'then
  full_pad={}
  if sourceUpdates-flower.M_moves>=25 then
   assert(sourceUpdates-flower.M_moves==25,'Exactly25 source movements after real M')
   requirePickup(flower.pickups and flower.pickups.M,25)
   flower.M_resume=25;full_part='approach';full_step=0;full_last=q.completed_Main-1;flowerPhase('travel')
  else return end
 end
 if item then
  assert(ram(L.PowerUpType+item.slot)==1,'Actual complete spawn chain chose Flower')
  flower.born=flower.born or{Main=q.completed_Main,item=item,x=x,y=y}
  if item.state>=128 then flower.mature=flower.mature or{Main=q.completed_Main,item=item,x=x,y=y}end
 end
 if engine==9 then full_pad={};return end
 if flags==7 and engine==8 and r('GuestPowerupActive')==0 then
  assert(r('PlayerStatus')==2 and flower.born and flower.mature,'Mature real Flower and original flags7')
  flower.F_moves=flower.F_moves or sourceUpdates;flower.resume=sourceUpdates-flower.F_moves;full_pad={}
  if flower.resume==25 then
   flower.final={x=x,y=y,flags=flags,status=r('PlayerStatus'),lives=r('NumberofLives'),moves=sourceUpdates}
   requirePickup(flower.pickups and flower.pickups.F,25)
   flower.actual_post_F_moves=actualMoves-flower.pickups.F.grant.state.moves
   assert(flower.actual_post_F_moves==25,'Exactly25 actual post-Flower movement entries')
   finish(true,'Genuine earned Mushroom then Flower and25 actual movement calls');return
  end
  return
 end
 if flower.phase=='travel'then
  if not flower.target then
   local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
   for wx=math.floor(math.max(camera,1104)/16)*16,math.min(camera+224,x+160,1376),16 do
    for yy=80,160,16 do local _,tile=full_solid(wx+4,yy)
     if tile==0xc1 and(not flower.target or wx<flower.target.x)then flower.target={x=wx,y=yy}end
    end
   end
  end
  assert(x<1376,'Actual first Flower block before next pit')
  if flower.target and x>=flower.target.x-32 and y>=flower.target.y+16 and r('Player_State')==0 then
   flowerPhase('align');full_pad={}
  else return full_tick_base(finish)end
 end
 if flower.phase=='align'then
  full_pad={right=x<flower.target.x+1,left=x>flower.target.x+3}
  if x>=flower.target.x+1 and x<=flower.target.x+3 and full_normal_jump_ready(actor)and full_state(0x301)&128==0 then
   flowerPhase('bump');full_pad={a=true}
  end
 elseif flower.phase=='bump'then
  full_pad={a=flower.age<25}
  if item then
   local left=flower.target.x
   for _=1,8 do if full_solid(left-12,flower.target.y)then left=left-16 else break end end
   flower.runup=math.max(left-96,1144);flowerPhase('mount');full_pad={}
  elseif flower.age>80 then error('Real source head did not release Flower')end
 elseif flower.phase=='mount'then
  if mountDefence(q,actor,x,y)then return end
  if not full_normal_jump_ready(actor)then full_pad={};return end
  if x>flower.runup+2 then full_pad={left=true}
  elseif x<flower.runup-2 then full_pad={right=true}
  elseif full_state(0x102+(identity==1 and 8 or 0))&64==0 then full_pad={right=true}
  elseif full_launch_ready(actor)and full_state(0x301)&128==0 and flower.mature then
   flower.base=q;flowerPhase('grow');full_pad={right=true,b=true}
  else full_pad={}end
 elseif flower.phase=='grow'then
  local takeoff;full_pad,takeoff=poweredGrowth(q,flower.base,flower.age)
  if flower.age>=5 then assert(q.launches>flower.base.launches,'Actual earned Flower-mount bubble launch')end
  if takeoff then flowerPhase('ride')end
  assert(flower.age<180,'Measured grown bubble window')
 elseif flower.phase=='ride'then
  local tx=item and item.x or flower.target.x
  full_pad={right=x<tx-2,left=x>tx+3,a=true}
  full_pad=poweredAir(q,flower.base)or full_pad
  if y<=flower.target.y-32 and r('Player_State')==0 then full_pad.a=false end
 end
end

local routeStarted=false
local function drive()
 if not game or done or pending then return end
 if not routeStarted then
  if not active()or r('Player_Y_Position')~=176 then return end
  routeStarted=true;full_begin()
 end
 full_tick(finish)
 pad=0;for name,bit in pairs({right=1,left=2,down=4,up=8,start=16,select=32,b=64,a=128})do if full_pad[name]then pad=pad|bit end end
end
local function tick()
 assert(sourceThisMain<=1 and sourceOutside==0,'Every source update belongs to one real Main')
 assert(r('NumberofLives')==2 and work(2,0xc300)==identity,'Living exact Bubble identity')
 assert(header(2)==cookie and header(3)==cookie,'Both complete current source cookies')
 sampleBubble();drive()
end
assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,'Exact current ROM identity')
local uiNative={{offset=536803,data="4cd5af"},{offset=536533,data="08284ceba7"},{offset=536093,data="bc61aa"},{offset=536264,data="bc61aa"}}
for _,h in ipairs(uiNative)do for k=1,#h.data,2 do assert(emu.read(h.offset+(k-1)//2,emu.memType.nesPrgRom)==tonumber(h.data:sub(k,k+1),16),"Exact native UI shim/table alias")end end

for _,h in ipairs(hooks)do if h.kind=='rom'then for k=1,#h.data,2 do assert(emu.read(h.offset+(k-1)//2,emu.memType.nesPrgRom)==tonumber(h.data:sub(k,k+1),16),'Current native hook preimage')end end end
emu.addMemoryCallback(guard(function()
 if not game or not active()or not mapped(F.GameLoop,emu.memType.nesPrgRom,hooks[1].offset)then return end
 assert(not pending,'Previous native Main must have a captured return')
 local s=emu.getState();local sp=s['cpu.sp'];pending={pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535,sp=(sp+2)&255};sourceThisMain=0
 local known=false;for _,pc in ipairs(returnPcs)do if pc==pending.pc then known=true end end;assert(known,'Unqualified native Main return caller')
 local key=string.format('%04X/SP%d',pending.pc,pending.sp);entries[key]=(entries[key]or 0)+1;enteredMain=enteredMain+1
end),emu.callbackType.exec,F.GameLoop)
emu.addMemoryCallback(guard(function()
 if game and active()and mapped(sourcePc,emu.memType.nesWorkRam,3*8192+(sourcePc&8191))then sourceUpdates=sourceUpdates+1;sourceThisMain=sourceThisMain+1;if not pending then sourceOutside=sourceOutside+1 end end
end),emu.callbackType.exec,sourcePc)
local function returned()
 if not pending then return end;local c=emu.getState();if c['cpu.pc']~=pending.pc or c['cpu.sp']~=pending.sp then return end
 local key=string.format('%04X/SP%d',pending.pc,pending.sp);returns[key]=(returns[key]or 0)+1
 pending=nil;updates=updates+1;tick()
end
for _,pc in ipairs(returnPcs)do emu.addMemoryCallback(guard(returned),emu.callbackType.exec,pc)end
local function wait(fn)for _=1,1800 do if fn()then return end;coroutine.yield()end;error('Native title/menu/ingress bound')end
local function press(bits)pad=bits;for _=1,4 do coroutine.yield()end;pad=0;for _=1,8 do coroutine.yield()end end
local route=coroutine.create(function()
 wait(function()return frame>=100 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Fresh native menu begins at slot0')
 for _=1,3 do press(4)end;press(1)
 assert(r('CrossoverMenuIndex')==25,'Real D-pad selects visible slot25')
 for _=1,identity+1 do press(32)end;assert(r('SelectedCharacter')==39,'Real Select resolves Bubble source owner')
 press(16);wait(function()return active()end)
 for _,h in ipairs(hooks)do if h.kind=='work'then for k=1,#h.data,2 do assert(emu.read(h.offset+(k-1)//2,emu.memType.nesWorkRam)==tonumber(h.data:sub(k,k+1),16),'Actual cold Bubble runtime code')end end end

 local code="202ab3";for k=1,#code,2 do assert(work(3,48920+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end
 local code="4c56b3";for k=1,#code,2 do assert(work(3,45754+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end
 local code="4c9bb3ea";for k=1,#code,2 do assert(work(3,43191+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end
 local code="4ce2b3ea";for k=1,#code,2 do assert(work(3,48479+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end
 local code="48ad20c30d30c30d40c30d50c30d60c30d70c3d01368a9058dc0c3a9508dc5c3a8a900a206e00660684c9cb848ad10000d11000d12000d13000d14000d1500d02c68a9008d68c08d6cc08d70c08d74c08d78c08d7cc0a9058dc0c3a97c8dc1c3a9388dc2c3a900a206b8e00660684cc2b848ad88c00d8cc00d90c00d94c00d98c00d9cc00da0c00da4c00da8c00dacc00db0c00db4c00db8c00dbcc00dc0c00d64c2d00c68a900a2c4a000b8384cfba868a288a0884cbba848ad68c00d6cc00d70c00d74c00d78c00d7cc00d88c00d8cc00d90c00d94c00d98c00d9cc00da0c00da4c00da8c00dacc00db0c00db4c00db8c00dbcc00dc0c0d00c68a900a2c4a000b8384c93bd68a268a0104c63bd";for k=1,#code,2 do assert(work(3,45866+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end
 game=true;phase='settle'
end)
emu.addEventCallback(guard(function()polled=true;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;if polled then physicalPolls=physicalPolls+1 end;polled=false
 if frame>40000 then finish(false,'Physical bound40000');return end
 if game then drive()end
 if coroutine.status(route)~='dead'then local ok,why=coroutine.resume(route);assert(ok,why)end
end),emu.eventType.endFrame)
