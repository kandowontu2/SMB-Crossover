-- Natural title -> Mr. Gimmick Select3 -> authored mushroom -> powered Goomba hit.
-- Root binds the exact ROM/script hashes. This script writes only controller input.
-- Private source observations use physical work RAM, independently of the C-window.
-- The exact d254 launch expects its original invalid tier store. A corrected
-- launch requires the authenticated successor cookie and native recovery.
local env=os.getenv
local rom=env('SMB_STDOUT_ROM_SHA')or''
local variant=tonumber(env('SMB_TEST_VARIANT')or'0')
local wantImages=env('SMB_STDOUT_IMAGES')=='1'
local oldPins={
 ['d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0']=true,
 ['47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b']=true
}
local newPins={
 ['19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936']=true,
 ['49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7']=true
}
local old=oldPins[rom]==true
local cookie=old and 'a72b01c0f80210577f684adf9ea78ed5' or 'a72b0194a989064ae62ef75a04986523'
local L={
 OperMode=0x771,OperMode_Task=0x773,GameEngineSubroutine=0x0f,
 SelectedCharacter=0x6002,CrossoverTitleDrawn=0x6004,DisableScreenFlag=0x775,
 CrossoverMenuState=0x7307,CrossoverMenuIndex=0x7309,FmAlts=0x5ffe,
 Player_X_Position=0x75,Player_PageLoc=0x5c,Player_Y_Position=0xbd,
 Player_Y_HighPos=0xa4,Player_State=0x1e,NumberofLives=0x75f,
 WorldNumber=0x764,LevelNumber=0x761,AreaAddrsLOffset=0x754,
 CheatStartLevel=0x7ffc,CheatInvincible=0x7ffb,
 ScreenLeft_X_Pos=0x71f,ScreenLeft_PageLoc=0x71d,SavedJoypadBits=0xdc,
 Enemy_Flag=0x10,Enemy_ID=0x17,Enemy_State=0x1f,Enemy_X_Position=0x76,
 Enemy_PageLoc=0x5d,Enemy_Y_Position=0xbe,PowerUpType=0x34,
 PlayerStatus=0x75b,GuestPowerupActive=0x6bfd,GuestPowerupAge=0x6bfe,
 InjuryTimer=0x79b,TimerControl=0x74a,Square2SoundQueue=0x104,FloateyNum_Control=0x10d,
 R2=0x5,R6=0x9,R7=0xa,ColumnSets=0x721,AreaParserTaskNum=0x722,
 CurrentPageLoc=0x728,CurrentColumnPos=0x729,BlockBufferColumnPos=0x4a0,MTileAttribute=0xef36
}
local frame,updates,completed,polls,activeUpdates=0,0,0,0,0
local stopped,gameplay,mainLive,requestedFinish=false,false,nil,nil
local padBits,firstCold,lastState=0,nil,nil
local calls,events,imageQueue,imageTags={},{},{},{}
local phase,epoch,jumpStarted,jumpUntil='opening',0,-100,-1
local block,birth,mature,collection,transformed,injury,recovered
local recoveryUpdates,transformationTicks=0,0
local jumps,stores,inputChanges,returns,pending={},{},{},{},{}
local lastBits,collectionSound=nil,nil
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
local function signed24(at)
 local n=source(at)+256*source(at+1)+65536*source(at+2)
 return n>=0x800000 and n-0x1000000 or n
end
local function actor(i)
 return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i),
  kind=r('PowerUpType',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}
end
local function state()
 return{frame=frame,Main=updates,completed=completed,active_updates=activeUpdates,phase=phase,epoch=epoch,
  mode=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine'),
  x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),
  state=r('Player_State'),lives=r('NumberofLives'),world=r('WorldNumber'),level=r('LevelNumber'),
  camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),selected=r('SelectedCharacter'),
  source_x={source(0x70),source(0x71),source(0x72)},source_y={source(0x73),source(0x74),source(0x75)},
  source_flags=source(0x30),source_height=source(0x42),ready=source(0x119),frame_status=source(0x116),
  saved=r('SavedJoypadBits'),header2=header(2),header3=header(3),
  vx=signed24(0x20),vy=signed24(0x60),source_tick=source(0x92),
  status=r('PlayerStatus'),powered=r('GuestPowerupActive'),age=r('GuestPowerupAge'),
  timer=r('TimerControl'),injury_timer=r('InjuryTimer')}
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
  bounds={physical_frames=5500,logical_updates=3000,route_updates=1500},
  first_active_1_1=firstCold,terminal=s,calls=calls,cadence=cadence,physics=physics,
  events=events,image_tags=imageTags,jumps=jumps,inputs=inputChanges,
  authored_block=block,mushroom_birth=birth,mature=mature,collection=collection,
  transformation_ticks=transformationTicks,transformed=transformed,injury=injury,
  native_status_stores=stores,recovery_updates=recoveryUpdates,recovered=recovered,
  expected_old_negative=old,
  scope='Natural Mr. Gimmick Select3, authored mushroom, actual 60-update growth and deliberate native enemy contact.'}))
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
local function onReturn(cpu,action)
 local pc,sp=stackReturn(cpu)
 assert(#pending<8,'Bounded synchronous callback returns')
 pending[#pending+1]={pc=pc,sp=sp,action=action}
 if returns[pc]then return end;returns[pc]=true
 emu.addMemoryCallback(guarded('native callback return',function()
  local c=emu.getState()
  for i=#pending,1,-1 do
   local item=pending[i]
   if item.pc==c['cpu.pc']and item.sp==c['cpu.sp']then
    table.remove(pending,i);item.action(c)
   end
  end
 end),emu.callbackType.exec,pc)
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
 assert(y>=32 and y<240 and r('ColumnSets')==255,'Native controller terrain bounds')
 local parser,page,col=r('AreaParserTaskNum'),r('CurrentPageLoc'),r('CurrentColumnPos')
 assert(parser<8 and col<16 and r('BlockBufferColumnPos')==(page&1)*16+col,'Native ring cursor')
 local first=r('ScreenLeft_PageLoc')*16+(r('ScreenLeft_X_Pos')>>4)
 local limit=page*16+col+((parser&3)~=0 and 1 or 0)
 local column=x>>4
 assert(limit>first and limit-first<=32 and column>=first and column<limit,'Native queryable terrain interval')
 local at=0x300+((x>>8)&1)*208+((y>>4)-2)*16+(column&15)
 return r('MTileAttribute',read(at))&1~=0
end
local function requestJump(reason,s)
 assert(s.state==0 and s.source_flags&8~=0 and #jumps<24,'Original ready jump request')
 jumpStarted,jumpUntil=epoch,epoch+20
 jumps[#jumps+1]={reason=reason,requested=s}
end
local function drive()
 if not gameplay or requestedFinish then return end
 local s=state()
 assert(s.selected==43 and s.lives==2,'Native selected owner/lives')
 assert(s.world==0 and s.level==0 and r('AreaAddrsLOffset')==5,'Native1-1 area')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'No cheats')
 if not firstCold then
  firstCold=s;assert(s.x==40,'Native starting X40');queueImage('first_active_original_Sonic')
 end
 activeUpdates=activeUpdates+1;assert(activeUpdates<=1500,'Sonic route bound1500')
 if lastState then
  local dx,dc=s.x-lastState.x,s.camera-lastState.camera
  physics.ordinary_loops=physics.ordinary_loops+1
  physics.maximum_world_step=math.max(physics.maximum_world_step,dx)
  physics.minimum_world_step=math.min(physics.minimum_world_step,dx)
  physics.maximum_camera_step=math.max(physics.maximum_camera_step,dc)
  physics.minimum_camera_step=math.min(physics.minimum_camera_step,dc)
 end
 lastState=s
 assert(s.header2==cookie and s.header3==cookie,'Authenticated Sonic headers')
 if phase=='opening'then
  if s.x<200 then setPad(activeUpdates>4 and 1 or 0);return end
  assert((calls.OriginalSonicFrame or 0)>=20 and calls.SonicHostConstruct==1,'Original opening motor')
  phase='approach'
 end
 local item,goomba
 for i=0,5 do
  local a=actor(i)
  if a.flag==1 and a.id==46 then item=a end
  if a.flag~=0 and a.id==6 and a.x>=s.x and a.x-s.x<=56 then goomba=a end
 end
 if item then
  if not birth then assert(block and item.kind==0,'Authored mushroom birth');birth={actor=item,player=s}end
  if not mature and item.state&128~=0 then mature={actor=item,player=s}end
 end
 if collection and not transformed and s.powered==0 then
  assert(transformationTicks==60 and s.engine==8 and s.status==1 and s.timer==0,'Actual 60-update transformation')
  transformed=s;phase='seek_hit'
 end
 if injury then
  assert(#stores==1,'Single native power tier write')
  if old then
   assert(stores[1].a==43 and stores[1].carry==0 and s.status==43 and s.engine==10 and s.timer==255,'Exact old native tier43 corruption')
   requestedFinish={ok=true,why='Exact prior Sonic powered injury wrote tier43'};setPad(0);return
  end
  assert(stores[1].a==0 and stores[1].carry==0 and s.status==0,'Corrected native tier0 store')
  if s.engine==10 then
   recoveryUpdates=recoveryUpdates+1
   assert(s.source_tick==injury.player.source_tick,'Original motor frozen during native injury')
  elseif not recovered then
   assert(s.engine==8 and s.timer==0 and recoveryUpdates==55,'Native 55-update injury recovery')
   recovered=s;phase='resume'
  end
  if recovered and s.x>=recovered.x+16 then
   assert((s.source_tick-recovered.source_tick)&255>=6,'Original motion resumes after injury')
   queueImage('Sonic_native_injury_recovered');requestedFinish={ok=true,why='Earned mushroom, genuine hit and corrected tier0 recovery'}
   setPad(0);return
  end
 end
 local bits=0
 local ready=s.state==0 and s.source_flags&8~=0
 if phase=='approach'then
  bits=1
  if ready and goomba then requestJump('first_Goomba',s);phase='hop_brake' end
 elseif phase=='hop_brake'then
  if s.x<282 then bits=1 elseif s.vx>0 then bits=2 else phase='hop_land' end
 elseif phase=='hop_land'then
  if ready and s.y==176 then phase='under_block' end
 elseif phase=='under_block'then
  if s.x<325 then bits=1 elseif s.x>336 then bits=2
  elseif ready and epoch-jumpStarted>24 then requestJump('authored_mushroom_block',s) end
 elseif(phase=='seek_hit'and not injury)or phase=='resume'then
  bits=1
  if ready and epoch-jumpStarted>24 then
   for _,ahead in ipairs({24,36,48})do
    if solid(s.x+ahead,s.y+31)then requestJump(recovered and 'recovery_pipe' or 'pipe',s);break end
   end
  end
 end
 if item and not collection then
  phase='mushroom';local gap=item.x-s.x
  bits=gap>6 and 1 or gap< -6 and 2 or 0
  if ready and epoch-jumpStarted>24 and math.abs(gap)<=30 and item.y<s.y-12 then requestJump('rising_mushroom',s) end
 end
 if epoch<jumpUntil and s.engine==8 and(not injury or recovered)then bits=bits|128 end
 if bits~=lastBits then
  assert(#inputChanges<128,'Bounded input changes');inputChanges[#inputChanges+1]={epoch,bits};lastBits=bits
 end
 epoch=epoch+1;setPad(bits)
end
local function install()
 assert(variant==0,'Sonic script SMB_TEST_VARIANT must0')
 assert(old or newPins[rom],'Exact pinned injury predecessor/successor SHA')
 hook(0x82d9,function(pc)return native(pc,126)end,'GameLoop',function(cpu)
  assert(read(0x82d9)==0xa9 and read(0x82da)==0xff and read(0x82db)==0x8d,'Actual Main opcode')
  assert(not mainLive,'Synchronous Main');updates=updates+1;assert(updates<=3000,'Main bound3000')
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
  {0xd1cf,2,'MetaDraw'},{0xbfd2,3,'MetaFeet'},{0xd0c3,2,'MetaBounds'}})do
  hook(q[1],function(pc)return private(pc,q[2])end,q[3],function()end)
 end
 hook(0x9ef5,function(pc)return native(pc,126)end,'PlayerHeadCollision',function(c)
  if gameplay and c['cpu.a']==0xc1 then
   assert(not block,'Unique authored mushroom head contact')
   block={tile=0xc1,player=state(),r2=r('R2'),r6=r('R6'),r7=r('R7')}
   assert(block.r2==112 and block.r6==213 and block.r7==3,'Actual mushroom block pointer')
  end
 end)
 hook(0x9b28,function(pc)return native(pc,126)end,'HandlePowerUpCollision',function(c)
  if not gameplay then return end
  local item=actor(c['cpu.x']);local player=state()
  assert(block and birth and mature and not collection,'Unique mature authored mushroom')
  assert(item.flag==1 and item.id==46 and item.kind==0 and item.state&128~=0,'Actual mature mushroom actor')
  collectionSound=0
  onReturn(c,function()
   assert(r('Enemy_Flag',item.slot)==0 and r('FloateyNum_Control',item.slot)==6,'Native erase and score')
   assert(collectionSound>0,'Actual pickup SFX20 store')
   assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('GameEngineSubroutine')==9,'Actual hosted collection')
   collection={actor=item,player=player,sound_writes20=collectionSound};collectionSound=nil
  end)
 end)
 emu.addMemoryCallback(guarded('native pickup sound',function(_,value)
  if collectionSound and value==0x20 then collectionSound=collectionSound+1 end
 end),emu.callbackType.write,L.Square2SoundQueue)
 hook(0xb299,function(pc)return native(pc,10)end,'GuestPowerupUpdate',function(c)
  if not gameplay or r('GuestPowerupActive')==0 then return end
  assert(collection and transformationTicks<60 and r('GuestPowerupAge')==transformationTicks,'Native transformation clock')
  transformationTicks=transformationTicks+1
  if transformationTicks==60 then onReturn(c,function()
   assert(r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('PlayerStatus')==1,'Native growth completion')
  end)end
 end)
 hook(0x9771,function(pc)return native(pc,126)end,'ForceInjury',function(c)
  if not gameplay then return end
  local enemy=actor(c['cpu.x']);local player=state()
  assert(transformed and not injury and player.status==1,'Injury must follow earned growth')
  assert(enemy.flag==1 and enemy.id==6 and enemy.state<2,'Actual live Goomba injury')
  injury={actor=enemy,player=player};queueImage('Sonic_powered_Goomba_contact')
 end)
 hook(0x97a4,function(pc)return native(pc,126)end,'NativeStatusStore',function(c)
  assert(injury and #stores==0,'Actual native injury tier store')
  local p=c['cpu.ps']or c['cpu.p'];assert(p,'Actual processor flags')
  stores[#stores+1]={a=c['cpu.a'],carry=p&1}
 end)
 hook(0xd31b,function(pc)return private(pc,2)end,'SonicNativeInjuryDecline',function()
  assert(not old and injury,'Authenticated raw43 injury result')
 end)
 hook(0x97d6,function(pc)return native(pc,126)end,'KillPlayer',function()
  if gameplay then error('Unexpected native death before powered injury recovery')end
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
  frame=frame+1;assert(frame<=5500,'Physical frame bound5500')
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
