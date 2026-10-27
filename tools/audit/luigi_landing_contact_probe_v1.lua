-- Passive, startup-static contact diagnostics. No emulated writes or inputs.
local C=assert(LUIGI_LANDING_CONTACT_PROBE)
local R=assert(ROSTER_CONFIG)
local f=assert(io.open(R.prefix..'luigi-landing-contact.csv','w'))
local header='event,frame,cycle,line,dot,pc,bank,sp,a,x,y,p,stackReturn,objectOffset,character,variant,behavior,engine,playerX,playerY,yHigh,playerState,vx,vy,size,crouch,bboxCtrl,power,stompTimer,injuryTimer,noStomp,stompAllowed,frameCounter,screenX,enemyRelativeX,playerBoxHex,allEnemyBoxesHex,enemies,address,value,detail\n'
assert(f:write(header))
local rows,size,closed,foreign=0,#header,false,0
local bg,core=nil,nil
local bgCalls,bgReturns,coreCalls,coreReturns,injuries,stomps,kills=0,0,0,0,0,0,0
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or-1 end
local function within(s)return s['ppu.frameCount']>=C.first and s['ppu.frameCount']<=C.last end
local function ret(s)local sp=s['cpu.sp'];return(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)&65535 end
local function hex(at,n)local t={};for i=0,n-1 do t[#t+1]=string.format('%02x',emu.read(at+i,emu.memType.nesDebug))end;return table.concat(t)end
local function enemies()
 local a={}
 for i=0,5 do a[#a+1]=table.concat({i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('Enemy_X_Speed',i),r('Enemy_Y_Speed',i),r('Enemy_MovingDir',i),r('Enemy_CollisionBits',i),r('EnemyOffscrBitsMasked',i)},':')end
 return table.concat(a,';')
end
local function row(kind,s,at,value,detail)
 if closed or not within(s)then return end
 assert(r('SelectedCharacter')==8 and r('MarioVariant')==1 and r('CrossoverBehaviorVersion')==0,'Actual LuigiEasy probe owner')
 local a={kind,s['ppu.frameCount'],s['cpu.cycleCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc'],bank(s['cpu.pc']),s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],ret(s),r('ObjectOffset'),r('SelectedCharacter'),r('MarioVariant'),r('CrossoverBehaviorVersion'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('PlayerSize'),r('CrouchingFlag'),r('Player_BoundBoxCtrl'),r('PlayerStatus'),r('StompTimer'),r('InjuryTimer'),r('GuestBodyNoStomp'),r('GuestBodyStompAllowed'),r('FrameCounter'),r('Player_Rel_XPos'),r('Enemy_Rel_XPos'),hex(C.ram.BoundingBox_UL_Corner,4),hex(C.ram.BoundingBox_UL_Corner+4,24),enemies(),at or-1,value or-1,detail or''}
 local line=table.concat(a,',')..'\n';rows=rows+1;size=size+#line
 assert(rows<=2500 and size<=1048576,'Bounded80-frame passive contact CSV2500rows/1MiB')
 assert(f:write(line));f:flush()
end
local function hook(h,fn)
 emu.addMemoryCallback(function()
  if closed then return end;local s=emu.getState();if not within(s)then return end
  local actual=bank(h.pc);local yes=false;for _,b in ipairs(h.banks)do if b==actual then yes=true end end
  if not yes then foreign=foreign+1;return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual contact hook '..h.symbol)end
  fn(s)
 end,emu.callbackType.exec,h.pc)
end
hook(C.hooks.bg,function(s)
 row('PlayerBGCollision-entry',s)
 if ret(s)==C.hooks.after_bg.pc then assert(not bg,'No recursive owned BG call');bg={sp=s['cpu.sp'],caller=ret(s)};bgCalls=bgCalls+1 end
end)
hook(C.hooks.after_bg,function(s)
 if bg then assert(s['cpu.sp']==(bg.sp+2)%256,'Actual post-BG caller SP');bgReturns=bgReturns+1;bg=nil end
 row('PlayerCtrl-after-BG-before-guest-bridges',s)
end)
hook(C.hooks.core,function(s)
 if ret(s)==C.hooks.after_core.pc then assert(not core,'No recursive owned player/enemy core');core={sp=s['cpu.sp'],caller=ret(s)};coreCalls=coreCalls+1;row('PlayerEnemy-owned-collision-core-entry',s)end
end)
hook(C.hooks.after_core,function(s)
 if core then assert(s['cpu.sp']==(core.sp+2)%256,'Actual player/enemy core caller SP');coreReturns=coreReturns+1;core=nil end
 row('PlayerEnemy-after-core-carry-before-LDX',s)
end)
for _,key in ipairs({'player_enemy','contact','handle','body_after','water','injury_check','injury','force_injury','kill','stomp','set_engine'})do
 local name=key
 hook(C.hooks[name],function(s)
  if name=='injury'then injuries=injuries+1 elseif name=='stomp'then stomps=stomps+1 elseif name=='kill'then kills=kills+1 end
  row(C.hooks[name].symbol,s)
 end)
end
for _,name in ipairs({'Player_Y_Speed','Player_State','GameEngineSubroutine'})do
 local label=name
 emu.addMemoryCallback(function(at,v)if not closed then row('actual-write-'..label,emu.getState(),at,v,'value is actual bus store; RAM image is callback-time state')end end,emu.callbackType.write,C.ram[label])
end
emu.addEventCallback(function()if not closed then row('endFrame',emu.getState())end end,emu.eventType.endFrame)
return function()
 if closed then return{already_closed=true}end;closed=true;f:close()
 return{passive=true,first_frame=C.first,last_frame=C.last,rows=rows,logical_CSV_bytes=size,foreign_bank_callbacks=foreign,BG_calls=bgCalls,BG_returns=bgReturns,core_calls=coreCalls,core_returns=coreReturns,injury_entries=injuries,stomp_entries=stomps,kill_entries=kills,clipped_BG=bg~=nil,clipped_core=core~=nil,limits='Read-only80-frame entry/branch/bus-write snapshots. stackReturn is a genuine caller only at actual function entry; at internal branches it is the raw current top-word interpretation. Complete original hardware/input/death guards are unchanged. No native injury owner is inferred until these observations exist.'}
end
