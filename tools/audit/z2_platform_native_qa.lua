-- Native actor arena after real menu selection; no natural route/clear claim.
local C=assert(Z2_PLATFORM_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done,pending=false,false,false
local current=nil
local results,violations={},{}
local minSP=255
local prepared,finished,actorReturns=0,0,0
local stackWrites=0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then
  local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function world(n)return r(n..'_X_Position')+256*r(n..'_PageLoc')end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)local h=C.hooks[n];return bank(h.address)==h.physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n..' opcode')end end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'))
 for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
end
local log=assert(io.open(OUTPUT..'updates.csv','w'))
log:write('wall,case,age,x,y,state,vy,nativevy,air,platformX,platformY,secondY,flag,boxLeft,boxTop,boxRight,boxBottom,sp\n')
local function problem(message,data)
 local row={case=index,age=age,wall=wall,message=message,data=data};violations[#violations+1]=row
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close()
 capture('failure-'..index..'-'..age)
 local o=assert(io.open(OUTPUT..'failure-oam.bin','wb'));local s=assert(io.open(OUTPUT..'failure-sprite-staging.bin','wb'))
 for i=0,255 do o:write(string.char(emu.read(i,emu.memType.nesSpriteRam)));s:write(string.char(r('Sprite_Data',i)))end
 o:close();s:close()
 local visual=message=='Every native platform girder row reaches hardware OAM'
 if C.observe~=1 or not visual then assert(false,message)end
end
for _,pc in ipairs(C.foreign_jsr)do
 emu.addMemoryCallback(function()
  if not entered or done or not valid('Z2NativeSmallPlatformCollision')then return end
  local h=C.hooks.CrossoverLiftSecondY
  if bank(h.address)~=h.physical_bank then
   local st=emu.getState()
   problem('Relocated small-lift collision calls helper in wrong A bank',{pc=pc,target=h.address,actual_bank=bank(h.address),
     expected_bank=h.physical_bank,sp=st['cpu.sp'],a=st['cpu.a'],x=st['cpu.x'],y=st['cpu.y']})
  end
 end,emu.callbackType.exec,pc)
end
local align=nil
local writes=assert(io.open(OUTPUT..'player-y-writes.csv','w'));writes:write('wall,case,age,pc,bank,before,after,state,contacts,air,vy,flag\n')
emu.addMemoryCallback(function()
 if C.trap_alignment~=1 or not entered or done or not valid('L94F8')then return end
 if r('Player_Y_Position')%16==0 then return end
 local flags={};for i=0,5 do flags[#flags+1]=r('PlatformCollisionFlag',i)end
 align={before_y=r('Player_Y_Position'),player_state=r('Player_State'),contacts=r('Z2NativeContacts'),
   native_air=r('Z2NativeAir'),native_vy=r('Z2NativeVY'),native_pressed=r('Z2NativePressed'),
   saved_pad=r('SavedJoypadBits'),flags=flags,platform_y=r('Enemy_Y_Position',current.slot),
   platform_id=r('Enemy_ID',current.slot),slot=current.slot,entry_pc=C.hooks.L94F8.address}
end,emu.callbackType.exec,C.hooks.L94F8.address)
emu.addMemoryCallback(function(address,value)
 if entered and not done then
  local st=emu.getState();local before=r('Player_Y_Position')
  writes:write(table.concat({wall,index,age,st['cpu.pc'],bank(st['cpu.pc']),before,value,r('Player_State'),r('Z2NativeContacts'),r('Z2NativeAir'),r('Z2NativeVY'),r('PlatformCollisionFlag',current.slot)},',')..'\n');writes:flush()
  if C.trap_alignment==1 and before%16~=0 and value==(before&240) and age>0 and age<20 then
   local flags={};for i=0,5 do flags[#flags+1]=r('PlatformCollisionFlag',i)end
   problem('Native grounded origin quantized to 16px grid',{pc=st['cpu.pc'],actual_bank=bank(st['cpu.pc']),before_y=before,after_y=value,
    native_air=r('Z2NativeAir'),native_vy=r('Z2NativeVY'),player_state=r('Player_State'),contacts=r('Z2NativeContacts'),
    saved_pad=r('SavedJoypadBits'),native_pressed=r('Z2NativePressed'),flags=flags,slot=current.slot,platform_y=r('Enemy_Y_Position',current.slot)})
  end
 end
 if not align then return end
 local q=align;align=nil;q.after_y=value;q.pc=emu.getState()['cpu.pc'];q.actual_bank=bank(q.pc)
 if value~=q.before_y then problem('Native grounded AND F0 quantizes moving-platform origin',q)end
end,emu.callbackType.write,L.Player_Y_Position)
local savedNmi=nil
local nmiWindows={}
local function storeAt(pc,target)
 return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256
end
local function bankWindow(pc,target,shadow)
 if storeAt(pc,target)then
  return storeAt(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and storeAt(pc-5,shadow))
 end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and storeAt(pc+2,target)and storeAt(pc-3,shadow)
end
local stackLowest=0x200
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end
 stackWrites=stackWrites+1
 if address<stackLowest then
  local sp=emu.getState()['cpu.sp']
  if address==0x100+sp then stackLowest=address;minSP=math.min(minSP,(sp-1)%256)end
 end
end,emu.callbackType.write,0x180,0x1ff)
emu.addMemoryCallback(function(address,value)
 if entered and not done then assert(emu.getState()['cpu.sp']>=0x80,'Native stack does not cross lower-page guard')end
end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function()
 if not entered then return end
 bind('NonMaskableInterrupt')
 savedNmi={a=bank(0xa000),c=bank(0xc000),fields={},sp=emu.getState()['cpu.sp']}
 savedNmi.cpu_a=emu.getState()['cpu.a']
 savedNmi.shadow_a=r('CurrentBank')&127;savedNmi.shadow_c=r('CurrentBankC')&127
 local sp=savedNmi.sp
 savedNmi.resume=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 savedNmi.resume_bank=bank(savedNmi.resume);savedNmi.code={}
 for i=-8,8 do savedNmi.code[#savedNmi.code+1]=emu.read(savedNmi.resume+i,emu.memType.nesDebug)end
 savedNmi.a_window=savedNmi.a~=savedNmi.shadow_a and bankWindow(savedNmi.resume,0x5115,L.CurrentBank)
 savedNmi.c_window=savedNmi.c~=savedNmi.shadow_c and bankWindow(savedNmi.resume,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do savedNmi.fields[#savedNmi.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1;minSP=math.min(minSP,savedNmi.sp)
end,emu.callbackType.exec,C.hooks.NonMaskableInterrupt.address)
emu.addMemoryCallback(function()
 if not savedNmi then return end
 local wantA=savedNmi.a_window and savedNmi.shadow_a or savedNmi.a
 local wantC=savedNmi.c_window and savedNmi.shadow_c or savedNmi.c
 if bank(0xa000)~=wantA or bank(0xc000)~=wantC then
  local q=savedNmi;q.after_a=bank(0xa000);q.after_c=bank(0xc000)
  problem('NMI restores foreground A/C banks',q)
 end
 assert((r('CurrentBank')&127)==savedNmi.shadow_a and(r('CurrentBankC')&127)==savedNmi.shadow_c,'NMI restores foreground bank shadows')
 assert(emu.getState()['cpu.a']==savedNmi.cpu_a,'NMI restores foreground A before resumed mapper store')
 if savedNmi.a_window or savedNmi.c_window then nmiWindows[#nmiWindows+1]={wall=wall,case=index,age=age,resume=savedNmi.resume,
  a=savedNmi.a,shadow_a=savedNmi.shadow_a,c=savedNmi.c,shadow_c=savedNmi.shadow_c,code=savedNmi.code}end
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==savedNmi.fields[i],'NMI preserves five SMC operands')end
 assert(emu.getState()['cpu.sp']==savedNmi.sp,'NMI stack balanced before RTI');savedNmi=nil
end,emu.callbackType.exec,C.hooks.NmiReturn.address)
local function seed(q)
 assert(r('SelectedCharacter')==4 and r('Z2Variant')==1,'Actual selected Zelda II Link')
 w('CrossoverBehaviorVersion',1)
 w('WorldNumber',q.world or 1);w('LevelNumber',3);w('AreaNumber',3);w('AreaPointer',0x62);w('AreaType',3)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 local playerX=1249+(q.x or 127)
 w('Player_X_Position',playerX%256);w('Player_PageLoc',playerX//256);w('Player_Y_HighPos',1)
 w('Player_Y_Position',(q.second==1 and 176 or 112)-(q.fairy~=0 and 26 or 32)+(q.fairy~=0 and 1 or -1))
 w('Player_State',1);w('Player_Y_Speed',q.fairy~=0 and 0 or 2)
 w('Z2NativeVY',q.fairy~=0 and 0 or 2);w('Z2NativeGravityFraction',0);w('Z2NativeAir',1)
 for _,n in ipairs({'Z2NativeVX','Player_X_Speed','Player_X_Scroll','Z2NativeXFraction','Player_X_MoveForce',
 'Player_Y_MoveForce','Z2PreviousButtons','Z2HurtTimer','Z2AttackStage','Z2AttackTimer','CrouchingFlag',
 'SmCeilingHit','DisableCollisionDet','BlockBounceTimer','TimerControl','GameTimerExpiredFlag','EnemyFrenzyBuffer',
 'EnemyFrenzyQueue','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 w('PlayerSize',0);w('PlayerStatus',1);w('Player_CollisionBits',255);w('Z2NativeContacts',0)
 w('Z2NativeShield',1);w('Z2NativeWalkFace',1);w('Z2ActiveSpells',q.fairy)
 w('ScreenLeft_X_Pos',226);w('ScreenLeft_PageLoc',4);w('ScreenRight_X_Pos',225);w('ScreenRight_PageLoc',5)
 w('ScrollLock',1);w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 local s=q.slot
 local platX=1249+(q.px or 123)
 w('Enemy_Flag',1,s);w('Enemy_ID',q.ident,s);w('Enemy_X_Position',platX%256,s);w('Enemy_PageLoc',platX//256,s)
 w('Enemy_Y_HighPos',1,s);w('Enemy_BoundBoxCtrl',q.kind:find('small')and 4 or 5,s)
 w('Enemy_Y_Position',112,s);w('Enemy_State',q.kind:find('small')and 176 or 0,s)
 for _,n in ipairs({'Enemy_X_Speed','Enemy_Y_Speed','Enemy_YMoveForceFractional','Enemy_Y_MoveForce',
 'Enemy_X_MoveForce','PlatformCollisionFlag','XMovePrimaryCounter'})do w(n,0,s)end
 if q.kind:find('horizontal')then w('XMoveSecondaryCounter',12,s);w('XMovePrimaryCounter',q.kind:find('right')and 2 or 0,s)
 elseif q.kind:find('vertical')then w('YPlatformTopYPos',80,s);w('YPlatformCenterYPos',q.kind:find('up')and 96 or 128,s)end
 current={name=q.name,slot=s,carry=0,release=0,landed=false,startX=world('Player'),startPX=92+5*256,
          startPY=112,startSecond=176,actor=0,landingAge=-1,upward=0,edge=q.edge or '',oam_checks=0,history={},publications={}}
 current.startPX=platX
 age=0
 print('Z2_PLATFORM_SEED '..json({case=index,name=q.name,slot=s,wall=wall}))
end
local hooks,installedHooks={},{}
local function onReturn(entry,fn)
 local st=emu.getState();local sp=st['cpu.sp'];minSP=math.min(minSP,sp)
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=entry..':'..ret
 local rec={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 hooks[key]=rec
 if not installedHooks[key]then
  installedHooks[key]=true
  emu.addMemoryCallback(function()
   local q=hooks[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
   hooks[key]=nil;q.fn()
  end,emu.callbackType.exec,ret)
 end
end
emu.addMemoryCallback(function()
 if not valid('Z2PlatformBodyPrepare')or not entered or done then return end
 bind('Z2PlatformBodyPrepare')
 local old={};for i=0,23 do old[i+1]=r('EnemyBoundingBoxCoord',i)end
 onReturn('prepare',function()
  prepared=prepared+1
  for i=0,23 do if r('EnemyBoundingBoxCoord',i)~=old[i+1]then
   problem('Platform prepare changed native enemy rectangle',{offset=i,old=old[i+1],new=r('EnemyBoundingBoxCoord',i),slot=current.slot});break
  end end
 end)
end,emu.callbackType.exec,C.hooks.Z2PlatformBodyPrepare.address)
emu.addMemoryCallback(function()
 if not valid('Z2PlatformBodyFinish')or not entered or done then return end
 onReturn('finish',function()
  finished=finished+1
  local y=r('Player_Y_Position');local top=(y+(r('Z2NativeShield')~=0 and 0 or 4))%256
  if r('BoundingBox_UL_YPos')~=top or r('BoundingBox_DR_YPos')~=(y+29)%256 then
   problem('Platform finish restores source hurtbox',{y=y,top=r('BoundingBox_UL_YPos'),bottom=r('BoundingBox_DR_YPos')})
  end
 end)
end,emu.callbackType.exec,C.hooks.Z2PlatformBodyFinish.address)
local function actorReturn()
 actorReturns=actorReturns+1;current.actor=current.actor+1
 local q=C.cases[index];local s=q.slot;local flag=r('PlatformCollisionFlag',s)
 local support=q.kind:find('small')and(q.second==1 and 1 or 2)or s
 local attached=flag==support
 local py=q.second==1 and r('Enemy_State',s)or r('Enemy_Y_Position',s)
 local foot=r('Player_Y_Position')+(q.fairy~=0 and 26 or 32)
 if age>=1 and age<=19 and not q.edge and not attached then
  problem('Native support must remain continuous before release input',{flag=flag,support=support,foot=foot,platformY=py})
 end
 if q.edge then
  local rx=(world('Player')-(r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')))
  if rx<0 or rx>240 or r('BoundingBox_UL_XPos')>r('BoundingBox_DR_XPos')then
   problem('Native viewport clamp keeps body from wrapping horizontally',{rx=rx,left=r('BoundingBox_UL_XPos'),right=r('BoundingBox_DR_XPos')})
  end
  if q.edge:find('opposite')and attached then problem('No opposite-edge phantom platform contact',{flag=flag,rx=rx,platformX=r('Enemy_X_Position',s)})end
  if q.edge=='right-carry'and not attached then problem('Right viewport platform still supports visible body',{flag=flag,rx=rx,platformY=py,foot=foot})end
 end
 if age<=20 and attached then
  if not current.landed then current.landed=true;current.landingAge=age end
  if foot~=py then problem('Native platform carry aligns terrain foot',{foot=foot,platformY=py,flag=flag})end
  current.carry=current.carry+1
 end
 if age>=24 and not attached then current.release=current.release+1 end
 if age>=20 and r('Player_Y_Speed')>=128 and not attached then current.upward=current.upward+1 end
 if age==2 then current.horizontal_offset=world('Player')-(r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s))end
 if not q.edge and q.kind:find('horizontal')and age>=3 and age<=19 and world('Player')-(r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s))~=current.horizontal_offset then
  problem('Horizontal native carry preserves passenger offset',{offset=world('Player')-(r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s)),wanted=current.horizontal_offset})
 end
 local st=emu.getState();minSP=math.min(minSP,st['cpu.sp'])
 current.history[#current.history+1]={age=age,wall=wall,x=(r('Enemy_X_Position',s)-r('ScreenLeft_X_Pos'))%256,
  first=r('Enemy_Y_Position',s),second=r('Enemy_State',s),player_y=r('Player_Y_Position'),
  player_x=(world('Player')-(r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')))%256,
  pose=r('SmPosePtr')+256*r('SmPosePtr',1)}
 log:write(table.concat({wall,index,age,world('Player'),r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),r('Z2NativeVY'),r('Z2NativeAir'),
 r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s),r('Enemy_Y_Position',s),r('Enemy_State',s),flag,r('BoundingBox_UL_XPos'),r('BoundingBox_UL_YPos'),
 r('BoundingBox_DR_XPos'),r('BoundingBox_DR_YPos'),st['cpu.sp']},',')..'\n');log:flush()
end
local lastDMA,lastBodyPublication=nil,nil
local bodyLog=assert(io.open(OUTPUT..'body-publication.csv','w'));bodyLog:write('wall,case,age,event,ptr,c_bank,x,y\n')
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end
 local bytes={};for i=0,255 do bytes[i+1]=emu.read(value*256+i,emu.memType.nesDebug)end
 lastDMA={case=index,age=age,wall=wall,bytes=bytes,body=lastBodyPublication}
end,emu.callbackType.write,0x4014)
for _,name in ipairs({'RunLargePlatform','RunSmallPlatform'})do
 emu.addMemoryCallback(function()
  if not entered or done or not valid(name)then return end
  if emu.getState()['cpu.x']~=current.slot then return end
  bind(name);onReturn('actor',actorReturn)
 end,emu.callbackType.exec,C.hooks[name].address)
end
emu.addMemoryCallback(function()
 if not entered or done or not valid('RlNativeRenderDispatch')then return end
 local ptr=r('R0')+256*r('R1')
 bodyLog:write(table.concat({wall,index,age,'entry',ptr,bank(0xc000),r('R4'),r('R6')},',')..'\n');bodyLog:flush()
 if bank(0xc000)~=C.body_bank then return end
 -- Outlines-off copies the authentic descriptor to the existing RAM buffer.
 -- Bind the actual renderer input bytes, including Fairy's independent bob,
 -- rather than assuming the foreground pose pointer was already published.
 local size=emu.read(ptr,emu.memType.nesDebug);local parts={}
 if size==0 or size>64 or size%4~=0 then return end
 for i=1,size,4 do parts[#parts+1]={tile=emu.read(ptr+i,emu.memType.nesDebug),dy=emu.read(ptr+i+2,emu.memType.nesDebug),dx=emu.read(ptr+i+3,emu.memType.nesDebug)}end
 local authentic=nil
 for pose,rows in pairs(C.body_poses)do
  local same=#rows==#parts
  if same then for i,row in ipairs(rows)do local part=parts[i];if row.tile~=part.tile or row.dx~=part.dx or row.dy~=part.dy then same=false end end end
  if same then authentic=tonumber(pose);break end
 end
 if not authentic then return end
 local q={case=index,age=age,wall=wall,pose=authentic,actual_pointer=ptr,parts=parts,x=r('R4'),y=r('R6')}
 onReturn('native-body-publication',function()lastBodyPublication=q;bodyLog:write(table.concat({wall,index,age,'return',q.pose,bank(0xc000),q.x,q.y},',')..'\n');bodyLog:flush()end)
end,emu.callbackType.exec,C.hooks.RlNativeRenderDispatch.address)
local drawLog=assert(io.open(OUTPUT..'small-draw.csv','w'));drawLog:write('wall,case,age,event,x,y,offset,enemyY,secondY,offscreen,staging\n')
local renderWatch=nil
emu.addMemoryCallback(function()
 if not entered or done or not valid('CrossoverDrawSmallPlatform')then return end
 local function row(event)
  local st=emu.getState();local o={};for i=0,63 do
   local a=i*4;local py=r('Sprite_Data',a);local px=r('Sprite_Data',a+3)
   if py<240 then o[#o+1]=table.concat({i,px,py,r('Sprite_Data',a+1)},':')end
  end
  drawLog:write(table.concat({wall,index,age,event,st['cpu.x'],st['cpu.y'],r('ObjectOffset'),r('Enemy_Y_Position',current.slot),r('Enemy_State',current.slot),r('Enemy_OffscreenBits'),table.concat(o,'|')},',')..'\n');drawLog:flush()
 end
 local start=r('CurrentOAMOffset')
 row('entry');onReturn('small-draw',function()
  row('return')
  if C.trap_render==1 then renderWatch={address=L.Sprite_Data+start,expected=r('Sprite_Data',start),offset=start}end
 end)
end,emu.callbackType.exec,C.hooks.CrossoverDrawSmallPlatform.address)
emu.addMemoryCallback(function(address,value)
 if not renderWatch or address~=renderWatch.address or value<240 then return end
 local st=emu.getState();local q=renderWatch;renderWatch=nil
 problem('Rendered native small-lift row cleared before hardware DMA',{address=address,staging_offset=q.offset,before=q.expected,after=value,
  pc=st['cpu.pc'],actual_bank=bank(st['cpu.pc']),oam_cursor=r('CurrentOAMOffset'),rotation=r('GuestOamRotationActive')})
end,emu.callbackType.write,L.Sprite_Data,L.Sprite_Data+255)
emu.addMemoryCallback(function()
 if not valid('PauseSkip')or done or not native()then return end
 if not entered then
  if r('SelectedCharacter')~=4 or r('Z2Variant')~=1 or world('Player')<400 then return end
  bind('PauseSkip');entered=true;index=1;seed(C.cases[index]);return
 end
 age=age+1
 if age>=(C.cases[index].edge and 14 or 42)then
  local q=C.cases[index]
  if not q.edge then
   if not current.landed or current.carry<20 then problem('Native arena must land and carry every pre-input actor update',current)end
   if current.release<8 or current.upward<4 then problem('Native input must launch upward and release platform',current)end
   if q.kind:find('horizontal')and math.abs(r('Enemy_X_Position',q.slot)+256*r('Enemy_PageLoc',q.slot)-current.startPX)<5 then problem('Horizontal platform actually moves',current)end
   if q.kind:find('vertical')and math.abs(r('Enemy_Y_Position',q.slot)-current.startPY)<2 then problem('Vertical platform actually moves',current)end
  end
  results[#results+1]=current
  local compact={};for k,v in pairs(current)do if k~='history'and k~='publications'then compact[k]=v end end
  print('Z2_PLATFORM_CASE '..json(compact))
  index=index+1;if index>#C.cases then done=true;return end
  seed(C.cases[index])
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if native()then b.right=true
  elseif wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=4 then b.right=true
   elseif r('Z2Variant')~=1 then b.select=true else b.a=true end
  end
 elseif not done and not C.cases[index].edge and age>=20 and age<=30 then
  if C.cases[index].fairy~=0 then b.up=true else b.a=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<3300,'Bounded native platform arena')
 if entered and not done and(age==8 or age==16 or age==25 or age==32)then
  capture(string.format('case-%02d-age-%02d-wall-%04d',index,age,wall))
  local q=C.cases[index]
  if not q.edge and(age==8 or age==16)then
   assert(lastDMA and lastDMA.case==index,'Hardware publication belongs to this staged case')
   for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==lastDMA.bytes[i+1],'Hardware OAM exactly equals captured native DMA publication')end
   local function has(x,y,tile,attr)
    for i=0,63 do local a=i*4
     if lastDMA.bytes[a+1]==y and lastDMA.bytes[a+2]==tile and lastDMA.bytes[a+4]==x and(not attr or lastDMA.bytes[a+3]==attr)then return true end
    end
    return false
   end
   local found=nil
   -- The preserved failure established a3-update live-RAM/publication gap.
   -- Require exact coordinates in one of the last4 completed actor epochs,
   -- with the displayed authentic body from that very same epoch.
   for hi=#current.history,math.max(1,#current.history-3),-1 do
    local h=current.history[hi];local ys={h.first};local columns=q.kind:find('small')and 3 or 4
    if q.kind:find('small')then ys[#ys+1]=h.second end
    local good=true
    for _,y in ipairs(ys)do for col=0,columns-1 do if not has((h.x+col*8)%256,y,90,2)then good=false end end end
    local published=lastDMA.body
    local body=published and published.parts
    if not body or published.case~=index or published.x~=h.player_x or published.y~=h.player_y then good=false else for _,part in ipairs(body)do
     if not has((h.player_x+part.dx)%256,(h.player_y+part.dy)%256,part.tile,nil)then good=false end
    end end
    if good then found=h;break end
   end
   if not found then
    local o={};for i=0,63 do local a=i*4;if lastDMA.bytes[a+1]<240 then o[#o+1]={i,lastDMA.bytes[a+4],lastDMA.bytes[a+1],lastDMA.bytes[a+2],lastDMA.bytes[a+3]}end end
    problem('Every native platform girder row reaches hardware OAM',{dma_wall=lastDMA.wall,dma_age=lastDMA.age,live_age=age,oam=o,history=current.history,body=lastDMA.body})
   else
    current.publications[#current.publications+1]={frame=wall,dma_wall=lastDMA.wall,dma_age=lastDMA.age,actor_age=found.age,actor_wall=found.wall,
      first=found.first,second=q.kind:find('small')and found.second or -1,player_y=found.player_y,pose=lastDMA.body.pose,
      body_render_wall=lastDMA.body.wall,body_render_age=lastDMA.body.age}
    current.oam_checks=current.oam_checks+1
   end
  end
 end
 if done then
  local minimum=math.min(100,#C.cases*20)
  assert(nmis>minimum and prepared>minimum and finished>minimum and actorReturns>minimum,'Actual native platform/NMI paths executed')
  assert(minSP>0x20,'Native stack retains guard margin')
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json({passed=#violations==0,cases=results,violations=violations,nmis=nmis,
   mechanics_passed=true,known_visual_diagnostic=C.observe==1,
   prepared=prepared,finished=finished,actor_returns=actorReturns,min_sp=minSP,stack_writes=stackWrites,nmi_mapper_store_windows=nmiWindows,staged=true,
   scope='Real menu selection followed by explicit actor-boundary platform arenas. Native normal/Fairy large H/V and source independent small first/second lifts at slots0/3, landing/carry/jump-or-fly release, source hurtbox restoration, native enemy rectangle isolation, NMI bank/five-SMC and return-stack guards, PPU captures. No natural power acquisition, actual area route or campaign proof.'}));f:close()
  print('PASS native Zelda II platform arenas');log:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
