-- V3 observer: snapshot the immutable pose record at actual ThNaturalDrawDone.
-- V2 observer: validate descriptor-matched OAM cells and their consumed CHR slots.
-- Controller-only Thomas natural mushroom regression on a76 or its source repair.
-- Right+B toX325,8 Up+Right+B,Right+B toX400,coast; item uses slot4,
-- while existing original-jump support lifts retain their native actors.
-- Source state always uses physical work-RAM2; pickup SFX uses a write witness.
local rom=os.getenv('SMB_STDOUT_ROM_SHA') or ''
local L={OperMode=0x771,OperMode_Task=0x773,GameEngineSubroutine=0x0f,
 SelectedCharacter=0x6002,FmAlts=0x5fe5,CrossoverTitleDrawn=0x6004,DisableScreenFlag=0x775,
 CrossoverMenuState=0x7307,CrossoverMenuIndex=0x7309,FrameCounter=0x0e,
 Player_X_Position=0x75,Player_PageLoc=0x5c,Player_Y_Position=0xbd,Player_State=0x1e,
 NumberofLives=0x75f,PlayerStatus=0x75b,GuestPowerupActive=0x6bfd,
 GuestPowerupAge=0x6bfe,TimerControl=0x74a,Enemy_Flag=0x10,Enemy_ID=0x17,
 Enemy_State=0x1f,Enemy_X_Position=0x76,Enemy_PageLoc=0x5d,Enemy_Y_Position=0xbe,
 PowerUpType=0x34,Square2SoundQueue=0x104,FloateyNum_Control=0x10d,
 CurrentOAMOffset=0x6de,ObjectMetasprite=0x6e1,SmPosePtr=0x6b06,
 WorldNumber=0x764,LevelNumber=0x761,CheatInvincible=0x7ffb,CheatStartLevel=0x7ffc}
local frame,entries,completed,polls,padBits=0,0,0,0,0
local gameplay,stopped,mainLive=false,false,nil
local phase,step,routeEpoch='opening',0,0
local jump,collection,firstCold,birth,mature,recovered=nil,nil,nil,nil,nil,nil
local ticks,calls,events,inputs,returns,pending=0,{},{},{},{},{}
local collectionSound=nil
local upper,chr,dmas,hardwareChecks,recoveryHardware=0,{},0,0,0
local hardwareChrMode=0
local drawnBody=nil
local bodySnapshots=0
local hardwareLast,zeroFrames,previousCompleted=nil,0,0
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function source(offset)return emu.read(2*8192+offset,emu.memType.nesWorkRam)end
local function r(n,i)return read(assert(L[n],n)+(i or 0))end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function state()
 return {frame=frame,completed=completed,route_epoch=routeEpoch,phase=phase,step=step,
  x=wx(),y=r('Player_Y_Position'),native_state=r('Player_State'),status=r('PlayerStatus'),
  engine=r('GameEngineSubroutine'),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),
  timer=r('TimerControl'),lives=r('NumberofLives'),epoch=r('FrameCounter'),
  source_input=source(0x68),source_action=source(0x69)}
end
local function actor(i)return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),
 state=r('Enemy_State',i),kind=r('PowerUpType',i),
 x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function quote(v)return '"'..v:gsub('[%z\1-\31\\"]',function(c)
 if c=='"'then return '\\"'elseif c=='\\'then return '\\\\'end
 return string.format('\\u%04x',string.byte(c))end)..'"'end
local function json(v)
 local t=type(v);if t=='nil'then return 'null'elseif t=='string'then return quote(v)
 elseif t=='boolean'or t=='number'then return tostring(v)end
 assert(t=='table');local out={}
 if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=quote(tostring(k))..':'..json(x)end
 table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function note(kind,value)assert(#events<32);events[#events+1]={event=kind,value=value or state()}end
local function finish(ok,why)
 if stopped then return end;stopped=true;padBits=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=rom,
  controller_only=true,script_RAM_writes=false,output_files=0,Mesen_run=true,
  physical_frames=frame,logical_Main_entries=entries,completed_Main=completed,input_polls=polls,
  zero_completion_frames=zeroFrames,first_active=firstCold,mushroom_birth=birth,
  mushroom_mature=mature,collected=collection,powerup_ticks=ticks,resumed=recovered,
  calls=calls,hardware_checks=hardwareChecks,recovery_hardware_checks=recoveryHardware,last_hardware=hardwareLast,
  events=events,input_changes=inputs,terminal=state(),
  scope='Actual cold menu/controller first earned mushroom, native60-update transaction and16px movement. Existing original27px jump and native helper actors are retained; no life loss, state grants, flower/fullstage/all-powerup or audible-output claim.'}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name,fn)return function(...)
 if stopped then return end;local ok,why=pcall(fn,...)
 if not ok then finish(false,name..': '..tostring(why))end end end
local function setPad(bits)
 if bits~=padBits and #inputs<32 then inputs[#inputs+1]={frame=frame,completed=completed,
  route_epoch=routeEpoch,phase=phase,bits=bits}end;padBits=bits
end
local function mapped(pc,t,bank)
 local q=emu.convertAddress(pc)
 return q and q.memType==emu.memType[t] and q.address==bank*8192+(pc&8191)
end
local function native(pc,bank)return mapped(pc,'nesPrgRom',bank)end
local function private(pc)return mapped(pc,'nesWorkRam',3)end
local function stackReturn(cpu)
 local sp=cpu['cpu.sp'];return (read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535,(sp+2)&255
end
local function hook(pc,predicate,name,fn)
 emu.addMemoryCallback(guarded(name,function()
  if not predicate(pc)then return end;calls[name]=(calls[name]or 0)+1;fn(emu.getState())
 end),emu.callbackType.exec,pc)
end
local function onReturn(cpu,action)
 local pc,sp=stackReturn(cpu);assert(#pending<12);pending[#pending+1]={pc=pc,sp=sp,action=action}
 if not returns[pc]then returns[pc]=true
  emu.addMemoryCallback(guarded('native return',function()
   local c=emu.getState()
   for i=#pending,1,-1 do local p=pending[i]
    if p.pc==c['cpu.pc']and p.sp==c['cpu.sp']then table.remove(pending,i);p.action(c)end
   end
  end),emu.callbackType.exec,pc)
 end
end
local function drive()
 if not gameplay then return end
 local s=state();assert(r('SelectedCharacter')==10 and r('FmAlts')&0x44==0x40 and s.lives==2,'Exact Thomas owner/lives')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Actual1-1')
 assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0,'No cheats')
 assert(routeEpoch<1100,'Logical natural-route bound1100')
 for i=0,5 do local a=actor(i)
  if a.flag==1 and a.id==46 then
   assert(a.kind==0,'First earned mushroom identity')
   if not birth then birth=a;note('authored_item_birth',a)end
   if a.state&0x80~=0 and not mature then mature=a;note('native_item_mature',a)end
  end
 end
 local bits=0
 if phase=='opening'then
  bits=step<4 and 0 or step<36 and 1 or step<52 and 129 or 1
  step=step+1
  if step==60 then phase='approach';step=0 end
 elseif s.active~=0 then
  assert(collection,'Freeze requires actual native collection')
  assert(routeEpoch-collection.route_epoch<95,'Earned freeze recovery bound')
 elseif collection then
  assert(ticks==60 and s.status==1 and s.engine==8 and s.timer==0,'Exact earned recovery')
  recovered=recovered or s;bits=1
  if s.x>=collection.x+16 and hardwareChecks>0 and recoveryHardware>0 then finish(true,'Natural earned mushroom recovered and resumed16px');return end
 elseif phase=='approach'then
  bits=65;if s.x>=325 then phase='jump';jump=routeEpoch;bits=73 end
 elseif phase=='jump'then
  bits=routeEpoch-jump<8 and 73 or 65;if routeEpoch-jump>=8 then phase='park'end
 elseif phase=='park'then bits=s.x<400 and 65 or 0
 else error('Unknown Thomas route phase '..phase)end
 setPad(bits);routeEpoch=routeEpoch+1
end
local function bodyPatterns(page)
 local descriptor=drawnBody and drawnBody.descriptor or -1
 local result={descriptor=descriptor,parts={},CHR={},draw_snapshot=drawnBody,body_snapshots=bodySnapshots}
 for i=0,7 do result.CHR[i+1]=chr[i]or -1 end
 if not drawnBody then return false,result end
 local length=drawnBody.length
 result.length=length;if length==0 or length>64 or length%4~=0 then return false,result end
 local anchor=nil
 for i=0,length-1,4 do
  local cell=drawnBody.cells[i//4+1];local tile,attr,dy,dx=cell[1],cell[2],cell[3],cell[4]
  local found=nil
  for at=0,252,4 do
   local a=page*256+at;local y,t,v,x=read(a),read(a+1),read(a+2),read(a+3)
   if y<240 and t==tile and v&0xc3==attr&0xc3 and (not anchor or (x-dx)%256==anchor[1]and(y-dy)%256==anchor[2])then
    found={y=y,tile=t,attr=v,x=x};anchor={(x-dx)%256,(y-dy)%256};break
   end
  end
  if not found then
   result.missing_cell=i//4;result.expected_cell={tile=tile,attr=attr,dy=dy,dx=dx};result.visible_OAM={}
   for at=0,252,4 do local a=page*256+at;local y=read(a)
    if y<240 then result.visible_OAM[#result.visible_OAM+1]={index=at//4,y=y,tile=read(a+1),attr=read(a+2),x=read(a+3)}end
   end
   return false,result
  end
  local pattern=(found.tile&1)*4096+(found.tile&254)*16
  local slot=pattern//1024;local physical=chr[slot]
  found.pattern=pattern;found.slot=slot;found.physical=physical or -1
  result.parts[#result.parts+1]=found
  if not physical or physical<434 or physical>=442 then return false,result end
 end
 return true,result
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)setPad(bits);frames(4);setPad(0);frames(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Readiness bound')end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Initial menu0')
 for _,bits in ipairs({4,1,1,32,32})do press(bits)end
 assert(r('CrossoverMenuIndex')==10 and r('SelectedCharacter')==10 and r('FmAlts')&0x44==0x40,'Actual slot10 Thomas')
 note('natural_selection',{slot=10,owner=10,Select=2});press(16)
 ready(function()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end)
 gameplay=true;firstCold=state();assert(firstCold.x==40 and firstCold.status==0,'Cold native unpowered Thomas')
 drive();while not stopped do coroutine.yield()end
end)
guarded('setup',function()
 assert(#rom==64 and not rom:find('[^0-9a-f]'),'Exact runner ROM pin')
 hook(0x82d9,function(pc)return native(pc,126)end,'GameLoop',function(cpu)
  assert(not mainLive,'Synchronous Main');entries=entries+1;assert(entries<2500,'Main bound2500')
  local pc,sp=stackReturn(cpu);assert(pc==0x82be or pc==0x82d0,'Actual IdleLoop caller')
  mainLive={pc=pc,sp=sp}
 end)
 for _,pc in ipairs({0x82be,0x82d0})do
  hook(pc,function(at)return native(at,126)end,'GameLoopReturn',function(cpu)
   if mainLive and mainLive.pc==cpu['cpu.pc']and mainLive.sp==cpu['cpu.sp']then
    mainLive=nil;completed=completed+1;drive()
   end
  end)
 end
 hook(0x9b28,function(pc)return native(pc,126)end,'HandlePowerUpCollision',function(cpu)
  if not gameplay then return end
  local slot=cpu['cpu.x'];local a=actor(slot);assert(slot==4 and a.flag==1 and a.id==46 and a.kind==0 and a.state&0x80~=0,'Natural native mature actor')
  local before=state();local sound={writes20=0,clears=0,events={}};collectionSound=sound
  onReturn(cpu,function(c)
   assert(not collection and birth and mature,'Unique authored pickup')
   assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('GameEngineSubroutine')==9 and r('TimerControl')==255,'Actual hosted collection')
   collectionSound=nil
   note('native_collection_effects',{sound_witness=sound,slot=slot,flag=r('Enemy_Flag',slot),id=r('Enemy_ID',slot),
    floaty=r('FloateyNum_Control',slot),floaty_timer=read(0x12c+slot),
    square1=read(0xff),square2=r('Square2SoundQueue'),
    A=c['cpu.a'],X=c['cpu.x'],Y=c['cpu.y'],P=c['cpu.ps']or c['cpu.p'],player=state()})
   assert(r('Enemy_Flag',slot)==0 and r('FloateyNum_Control',slot)==6,'Native erase/floaty')
   assert(sound.writes20>0,'Native pickup SFX20 write witness')
   assert((c['cpu.ps']or c['cpu.p'])&1~=0,'Native accepted pickup')
   collection=before;collection.actor=a;note('native_mushroom_collection',collection)
  end)
 end)
 hook(0xb299,function(pc)return native(pc,10)end,'GuestPowerupUpdate',function(cpu)
  if not gameplay or r('GuestPowerupActive')==0 then return end
  assert(collection and ticks<60 and r('GuestPowerupAge')==ticks,'Exact native progression age')
  ticks=ticks+1;local terminal=ticks==60
  onReturn(cpu,function()
   if terminal then assert(r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('PlayerStatus')==1,'Native terminal transaction');note('freeze60_completed')
   else assert(r('GuestPowerupActive')==1 and r('GameEngineSubroutine')==9 and r('TimerControl')==255,'Native intermediate transaction')end
  end)
 end)
 hook(0xa375,private,'ThNaturalDrawDone',function()
  if not gameplay then return end
  assert(source(0x800)==167,'Actual Thomas constructor ready')
  local pose=source(0x846);assert(pose<42,'Actual original pose')
  local base=432*1024
  local lo=emu.read(base+1026+pose,emu.memType.nesChrRom)
  local hi=emu.read(base+1068+pose,emu.memType.nesChrRom)
  local descriptor=lo+256*hi;assert(descriptor>=0xd000 and descriptor<0xd402,'Immutable source descriptor')
  local at=base+descriptor-0xd000;local length=emu.read(at,emu.memType.nesChrRom)
  assert(length>0 and length<=64 and length%4==0,'Original descriptor length')
  local cells={}
  for i=0,length-1,4 do
   cells[#cells+1]={emu.read(at+1+i,emu.memType.nesChrRom),emu.read(at+2+i,emu.memType.nesChrRom),
    emu.read(at+3+i,emu.memType.nesChrRom),emu.read(at+4+i,emu.memType.nesChrRom)}
  end
  bodySnapshots=bodySnapshots+1;drawnBody={descriptor=descriptor,pose=pose,length=length,cells=cells,frame=frame,completed=completed}
 end)
 hook(0xb5c0,private,'ThomasNativePowerupTick',function()end)
 hook(0xb5b2,private,'ThomasNativeMature',function()end)
 hook(0xa103,private,'ThMovement',function()end)
 emu.addMemoryCallback(guarded('native pickup sound write',function(_,value)
  if not collectionSound then return end
  if value==32 then collectionSound.writes20=collectionSound.writes20+1 end
  if value==0 then collectionSound.clears=collectionSound.clears+1 end
  if #collectionSound.events<8 then
   local cpu=emu.getState();local pc=cpu['cpu.pc'];local a=emu.convertAddress(pc)
   collectionSound.events[#collectionSound.events+1]={value=value,frame=frame,pc=pc,
    mapped=a and a.address or -1,memory=a and tostring(a.memType)or 'unmapped'}
  end
 end),emu.callbackType.write,L.Square2SoundQueue)
 emu.addMemoryCallback(guarded('CHR mode',function(_,value)hardwareChrMode=value end),emu.callbackType.write,0x5101)
 emu.addMemoryCallback(guarded('CHR upper',function(_,v)upper=(v&3)*256 end),emu.callbackType.write,0x5130)
 emu.addMemoryCallback(guarded('CHR banks',function(at,v)chr[at-0x5120]=v+upper end),emu.callbackType.write,0x5120,0x512b)
 emu.addMemoryCallback(guarded('hardware body DMA',function(_,page)
  if not gameplay then return end;dmas=dmas+1
  if dmas<4 or r('GameEngineSubroutine')~=8 or (collection and not recovered)then return end
  local aligned=r('CurrentOAMOffset')%4==0 and r('ObjectMetasprite')==0 and read(L.SmPosePtr)+256*read(L.SmPosePtr+1)==0xc84a and source(0x84a)==0
  local banks,body=bodyPatterns(page)
  local palette=emu.read(0x3f11,emu.memType.nesPpuDebug)==39 and emu.read(0x3f12,emu.memType.nesPpuDebug)==48 and emu.read(0x3f13,emu.memType.nesPpuDebug)==15
  local hud=true;for i,v in ipairs({29,17,24,22,10,28,36})do if emu.read(0x2042+i,emu.memType.nesPpuDebug)~=v then hud=false end end
  local lows,modes={},{};for i=0,7 do lows[i+1]=read(0x147+i);modes[i+1]=read(0x73e0+i)end
  hardwareLast={aligned=aligned,banks=banks,palette=palette,HUD=hud,frame=frame,
   upper=upper,CHR_mode=hardwareChrMode,shadow_lows=lows,shadow_modes=modes,body=body}
  assert(aligned and banks and palette and hud,'Original Thomas OAM/CHR/palette/HUD')
  hardwareChecks=hardwareChecks+1
  if recovered then recoveryHardware=recoveryHardware+1 end
 end),emu.callbackType.write,0x4014)
 emu.addEventCallback(guarded('inputPolled',function()
  polls=polls+1;local b=padBits;emu.setInput({right=b&1~=0,left=b&2~=0,down=b&4~=0,up=b&8~=0,start=b&16~=0,select=b&32~=0,b=b&64~=0,a=b&128~=0},0)
 end),emu.eventType.inputPolled)
 emu.addEventCallback(guarded('endFrame',function()
  frame=frame+1;assert(frame<4000,'Physical bound4000')
  if gameplay and completed==previousCompleted then zeroFrames=zeroFrames+1 end;previousCompleted=completed
  local ok,why=coroutine.resume(task);assert(ok,why)
 end),emu.eventType.endFrame)
end)()
