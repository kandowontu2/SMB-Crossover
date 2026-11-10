-- Natural title -> Mr. Gimmick Select3 -> original Sonic motor through 1-1.
-- Root binds the exact ROM/script hashes. This script writes only controller input.
-- Private source observations use physical work RAM, independently of the C-window.
-- The actual CPU route supplies the read-only terrain/enemy cues and A timing.
local env=os.getenv
local rom=env('SMB_STDOUT_ROM_SHA')or''
local variant=tonumber(env('SMB_TEST_VARIANT')or'0')
local wantImages=env('SMB_STDOUT_IMAGES')=='1'
local L={
 OperMode=0x771,OperMode_Task=0x773,GameEngineSubroutine=0x0f,
 SelectedCharacter=0x6002,CrossoverTitleDrawn=0x6004,DisableScreenFlag=0x775,
 CrossoverMenuState=0x7307,CrossoverMenuIndex=0x7309,FmAlts=0x5ffe,
 Player_X_Position=0x75,Player_PageLoc=0x5c,Player_Y_Position=0xbd,
 Player_Y_HighPos=0xa4,Player_State=0x1e,NumberofLives=0x75f,
 WorldNumber=0x764,LevelNumber=0x761,AreaAddrsLOffset=0x754,
 CheatStartLevel=0x7ffc,CheatInvincible=0x7ffb,
 ScreenLeft_X_Pos=0x71f,ScreenLeft_PageLoc=0x71d,SavedJoypadBits=0xdc,
 AreaType=0x753,Enemy_Flag=0x10,Enemy_ID=0x17,Enemy_State=0x1f,
 Enemy_X_Position=0x76,Enemy_PageLoc=0x5d,Enemy_Y_Position=0xbe,
 ColumnSets=0x721,AreaParserTaskNum=0x722,CurrentPageLoc=0x728,CurrentColumnPos=0x729,
 BlockBufferColumnPos=0x4a0,MTileAttribute=0xef36
}
local frame,updates,completed,polls,activeUpdates=0,0,0,0,0
local stopped,gameplay,mainLive,requestedFinish=false,false,nil,nil
local padBits,firstCold,lastState=0,nil,nil
local calls,events,imageQueue,imageTags={},{},{},{}
local flag,castle,entrance,active12=nil,nil,nil,nil
local jumps,lastJump,bestX,advancedAt={},-100,0,0
local priorCompleted,priorPolls=0,0
local cadence={catchup_updates=0,maximum_updates_per_frame=0,
 gameplay_physical_frames=0,gameplay_zero_update_frames=0,physical_frames_without_input_poll=0}
local physics={ordinary_loops=0,maximum_world_step=0,minimum_world_step=0,
 maximum_camera_step=0,minimum_camera_step=0}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function source(at,bank)return emu.read((bank or 2)*8192+(at&8191),emu.memType.nesWorkRam)end
local function r(n,i)return read(assert(L[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function active(s)return s.mode==1 and s.task==3 and s.engine==8 end
local function header(bank)
 local out={};for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',source(at,bank))end
 return table.concat(out)
end
local function state()
 return{frame=frame,Main=updates,completed=completed,active_updates=activeUpdates,
  mode=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine'),
  x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),
  state=r('Player_State'),lives=r('NumberofLives'),world=r('WorldNumber'),level=r('LevelNumber'),
  area=r('AreaAddrsLOffset'),area_type=r('AreaType'),
  camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),selected=r('SelectedCharacter'),
  source_x={source(0x70),source(0x71),source(0x72)},source_y={source(0x73),source(0x74),source(0x75)},
  source_flags=source(0x30),source_height=source(0x42),ready=source(0x119),frame_status=source(0x116),
  source_vy={source(0x60),source(0x61),source(0x62)},
  saved=r('SavedJoypadBits'),header2=header(2),header3=header(3)}
end
local function quote(s)
 return'"'..s:gsub('[%z\1-\31\\"]',function(c)
  if c=='"'then return'\\"'elseif c=='\\'then return'\\\\'end
  return string.format('\\u%04x',string.byte(c))
 end)..'"'
end
local function json(v)
 local t=type(v)
 if t=='string'then return quote(v)end
 if t=='nil'then return'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 assert(t=='table','JSON type '..t)
 local out={}
 if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=quote(tostring(k))..':'..json(x)end
 table.sort(out);return'{'..table.concat(out,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;padBits=0
 local good,s=pcall(state);if not good then s={snapshot_error=tostring(s)}end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=rom,
  ROM_pin_supplied_by_runner=true,variant=variant,character='Sonic SMS',controller_only=true,
  script_RAM_writes=false,save_load_or_cheats=false,output_files=0,
  physical_frames=frame,logical_Main_entries=updates,completed_Main=completed,input_polls=polls,
  bounds={physical_frames=12000,logical_updates=6000,active_updates=3500},
  first_active_1_1=firstCold,terminal=s,calls=calls,cadence=cadence,physics=physics,
  native_flag=flag,native_castle=castle,native_entrance=entrance,active_1_2=active12,
  events=events,jump_events=jumps,image_tags=imageTags,
  scope='Natural title/menu Gimmick Select3 through native 1-1 flag and castle to active underground 1-2. Controller-only physical route.'}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name,fn)
 return function(...)
  if stopped then return end
  local ok,why=pcall(fn,...);if not ok then finish(false,name..': '..tostring(why))end
 end
end
local function setPad(bits)padBits=bits end
local function buttons(bits)
 return{right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,up=bits&8~=0,
  start=bits&16~=0,select=bits&32~=0,b=bits&64~=0,a=bits&128~=0}
end
local function mapped(pc,kind,physical)
 local a=emu.convertAddress(pc);return a and a.memType==emu.memType[kind]and a.address==physical
end
local function native(pc,bank)return mapped(pc,'nesPrgRom',bank*8192+(pc&8191))end
local function private(pc,bank)return mapped(pc,'nesWorkRam',bank*8192+(pc&8191))end
local function stackReturn(s)
 local sp=s['cpu.sp'];return(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535,(sp+2)&255
end
local function hook(pc,predicate,name,fn)
 emu.addMemoryCallback(guarded(name,function()
  if not predicate(pc)then return end
  calls[name]=(calls[name]or 0)+1;fn(emu.getState())
 end),emu.callbackType.exec,pc)
end
local function queueImage(tag)
 if wantImages and #imageQueue+#imageTags<2 then imageQueue[#imageQueue+1]=tag end
end
local function solid(x,y)
 assert(y>=32 and y<240,'Controller terrain vertical bounds')
 assert(r('ColumnSets')==255,'Native initial columns ready')
 local phase,page,col=r('AreaParserTaskNum'),r('CurrentPageLoc'),r('CurrentColumnPos')
 assert(phase<8 and col<16 and r('BlockBufferColumnPos')==(page&1)*16+col,'Native ring cursor')
 local first=r('ScreenLeft_PageLoc')*16+(r('ScreenLeft_X_Pos')>>4)
 local limit=page*16+col+((phase&3)~=0 and 1 or 0)
 local column=x>>4
 assert(limit>first and limit-first<=32 and column>=first and column<limit,'Controller terrain queryable interval')
 local at=0x300+((x>>8)&1)*208+((y>>4)-2)*16+(column&15)
 return r('MTileAttribute',read(at))&1~=0
end
local function jumpReason(s)
 for i=0,5 do
  local dx=pos('Enemy_X_Position','Enemy_PageLoc',i)-s.x
  if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)<21 and r('Enemy_State',i)<2 and
     dx>=0 and dx<=56 and math.abs(r('Enemy_Y_Position',i)-s.y-8)<24 then return 'enemy' end
 end
 local foot=s.y+32
 for _,ahead in ipairs({24,36,48})do if solid(s.x+ahead,foot-1)then return 'wall' end end
 for y=foot+1,239,16 do if solid(s.x+36,y)then return nil end end
 return 'ledge'
end
local function drive()
 if not gameplay or requestedFinish then return end
 local s=state()
 assert(s.selected==43 and s.lives==2,'Native selected owner/lives')
 assert(s.world==0 and s.level<=1,'Native world/level')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats')
 if s.level==0 and s.engine==4 and s.x>=3000 and not flag then
  flag=s;queueImage('Sonic_native_1_1_flag')
 end
 if s.level==0 and s.engine==5 and s.x>=3000 and not castle then castle=s end
 if s.level==1 and s.engine==7 and not entrance then entrance=s end
 if s.level==1 and active(s)then
  assert(flag and castle and entrance,'Native flag/castle/entrance witnesses')
  assert(s.area==0 and s.area_type==2,'Active underground 1-2 area')
  assert((calls.OriginalSonicFrame or 0)>=1000 and(calls.SonicHostConstruct or 0)==1,'Original frames and once-only 1-1 constructor')
  assert((calls.MetaFeet or 0)>0 and(calls.MetaDraw or 0)>0,'Owned native feet/body')
  assert(s.header2=='a72b01c0f80210577f684adf9ea78ed5'and s.header3==s.header2,'Authenticated Sonic headers')
  active12=s;queueImage('Sonic_active_1_2');requestedFinish={ok=true,why='Original Sonic cleared 1-1 and entered active 1-2'}
  setPad(0);return
 end
 if not active(s)then lastState=nil;setPad(0);return end
 assert(s.level==0 and s.area==5,'Native1-1 area')
 if not firstCold then
  firstCold=s;assert(s.x==40,'Native starting X40')
 end
 if lastState then
  local dx,dc=s.x-lastState.x,s.camera-lastState.camera
  physics.ordinary_loops=physics.ordinary_loops+1
  physics.maximum_world_step=math.max(physics.maximum_world_step,dx)
  physics.minimum_world_step=math.min(physics.minimum_world_step,dx)
  physics.maximum_camera_step=math.max(physics.maximum_camera_step,dc)
  physics.minimum_camera_step=math.min(physics.minimum_camera_step,dc)
 end
 lastState=s
 if s.x>bestX then bestX=s.x;advancedAt=activeUpdates end
 assert(activeUpdates-advancedAt<120,'Sonic native route stalled')
 assert(s.frame_status==0,'Original frame unavailable')
 if #jumps>0 then
  local jump=jumps[#jumps]
  if not jump.sampled and s.saved&128~=0 then jump.sampled=s end
  if not jump.accepted and s.state==1 and s.source_vy[3]&128~=0 and s.saved&128~=0 then
   jump.accepted=s
  end
 end
 local bits=activeUpdates>3 and 1 or 0
 if s.state==0 and s.source_flags&8~=0 and activeUpdates-lastJump>24 then
  local why=jumpReason(s)
  if why then
   assert(#jumps<64,'Sonic route jump bound64');lastJump=activeUpdates
   jumps[#jumps+1]={reason=why,requested=s}
  end
 end
 if activeUpdates-lastJump<20 then bits=bits|128 end
 activeUpdates=activeUpdates+1;assert(activeUpdates<=3500,'Active-update bound3500')
 setPad(bits)
end
local function install()
 assert(variant==0,'Sonic script SMB_TEST_VARIANT must0')
 assert(#rom==64 and not rom:find('[^0-9a-f]'),'Exact lower-case ROM SHA supplied by root')
 hook(0x82d9,function(pc)return native(pc,126)end,'GameLoop',function(cpu)
  assert(read(0x82d9)==0xa9 and read(0x82da)==0xff and read(0x82db)==0x8d,'Actual Main opcode')
  assert(not mainLive,'Synchronous Main');updates=updates+1;assert(updates<=6000,'Main bound6000')
  local ret,sp=stackReturn(cpu);assert(ret==0x82be or ret==0x82d0,'Native IdleLoop/catchup caller')
  if ret==0x82d0 then cadence.catchup_updates=cadence.catchup_updates+1 end
  mainLive={ret=ret,sp=sp}
 end)
 for _,pc in ipairs({0x82be,0x82d0})do
  hook(pc,function(at)return native(at,126)end,'GameLoopReturn',function(cpu)
   if not mainLive or mainLive.ret~=cpu['cpu.pc']or mainLive.sp~=cpu['cpu.sp']then return end
   mainLive=nil;completed=completed+1;drive()
  end)
 end
 for _,q in ipairs({{0xbd7a,3,'SonicHostMain'},{0xbebb,3,'SonicHostConstruct'},
  {0xbf51,3,'SonicHostPowerup'},{0xbbb0,3,'OriginalSonicFrame'},
  {0xd1cf,2,'MetaDraw'},{0xbfd2,3,'MetaFeet'},{0xd0c3,2,'MetaBounds'},
  {0xd2e9,2,'SceneFeet'},{0xd2f5,2,'SceneSide'},{0xd301,2,'SceneHead'},{0xd310,2,'SceneBounds'}})do
  hook(q[1],function(pc)return private(pc,q[2])end,q[3],function()end)
 end
 hook(0x97d6,function(pc)return native(pc,126)end,'KillPlayer',function()
  if gameplay then error('Native injury/death before stage clear')end
 end)
 hook(0xd0ec,function(pc)return private(pc,2)end,'MetaDeath',function()
  if gameplay then error('Native fall before stage clear')end
 end)
 emu.addEventCallback(guarded('inputPolled',function()
  polls=polls+1;emu.setInput(buttons(padBits),0)
 end),emu.eventType.inputPolled)
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)setPad(bits);frames(4);setPad(0);frames(8)end
local function ready(predicate)
 for _=1,900 do if predicate()then return end;coroutine.yield()end
 error('Natural menu/gameplay readiness timeout')
end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Natural initial slot0')
 for _,bits in ipairs({4,4,4,1})do press(bits)end
 assert(r('CrossoverMenuIndex')==25 and r('FmAlts')==0,'Natural MrGimmick slot25')
 for _=1,3 do press(32)end
 assert(r('SelectedCharacter')==43 and r('FmAlts')==3,'Gimmick Select3 Sonic')
 events[#events+1]={event='Sonic_selected',index=25,Select=3,raw=43}
 press(16);ready(function()return active(state())end)
 gameplay=true;drive();while not stopped do coroutine.yield()end
end)
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function base64(bytes)
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
  out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1)
  local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1)
  j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1)or'='
  j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
guarded('setup',function()
 install()
 emu.addEventCallback(guarded('endFrame',function()
  frame=frame+1;assert(frame<=12000,'Physical frame bound12000')
  local count=completed-priorCompleted
  cadence.maximum_updates_per_frame=math.max(cadence.maximum_updates_per_frame,count)
  if gameplay then
   cadence.gameplay_physical_frames=cadence.gameplay_physical_frames+1
   if count==0 then cadence.gameplay_zero_update_frames=cadence.gameplay_zero_update_frames+1 end
   if polls==priorPolls then cadence.physical_frames_without_input_poll=cadence.physical_frames_without_input_poll+1 end
  end
  priorCompleted=completed;priorPolls=polls
  while #imageQueue>0 do
   local tag=table.remove(imageQueue,1);assert(#imageTags<2,'At most2 stdoutPNGs')
   local png=emu.takeScreenshot();assert(type(png)=='string'and png:sub(1,8)=='\137PNG\r\n\26\n','In-memory PNG')
   imageTags[#imageTags+1]={tag=tag,frame=frame,bytes=#png};print('SMB_NATIVE_IMAGE '..base64(png))
  end
  if requestedFinish then finish(requestedFinish.ok,requestedFinish.why);return end
  local ok,why=coroutine.resume(task);assert(ok,why)
 end),emu.eventType.endFrame)
end)()
