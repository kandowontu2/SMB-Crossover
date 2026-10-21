-- Explicit collision unit fixture, not a controller-only level clear.
-- Reconstructs the real33 water-coral contact immediately before the genuine
-- PlayerBGCollision parser. Every collision then runs with no geometry writes.
-- Mario0 is the independent native oracle for Luigi8, across mirrored contacts,
-- fractional guest-state sentinels, power forms, page seams and velocity paths.
local frame,index=0,0
local current,active,returnPC,entrySP,nativeCalls,wallCalls,positionWrites
local cases,controls={},{}
local characters=NATIVE_WALL_CONTROL_ONLY and{0}or{0,8}
for _,engine in ipairs({8,7})do for power=0,2 do
 for _,base in ipairs({192,208,2048})do for _,side in ipairs({1,2})do for _,offset in ipairs({62,64,65})do
  for _,motion in ipairs({'toward','stationary','away'})do for _,char in ipairs(characters)do
   cases[#cases+1]={engine=engine,power=power,base=base,side=side,offset=offset,motion=motion,char=char}
  end end
 end end end
end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local fields={'Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed',
 'Player_CollisionBits','SideCollisionTimer','Player_X_Scroll','GameEngineSubroutine',
 'MmVX','MmXFraction','MmVY','Player_State'}
local out=assert(io.open(OUTPUT..ROM_NAME..'-native-wall-corner.csv','w'))
out:write('case,character,engine,power,base,side,offset,motion,startX,endX,dx,nativeCalls,wallCalls,positionWrites,'..table.concat(fields,',')..'\n')
local function setup(q)
 current=q;nativeCalls=0;wallCalls=0;positionWrites=0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 local function block(wx,y)
  local off=(wx//256)%2*208+((y-32)//16)*16+(wx%256)//16
  w('Block_Buffer_1',0x69,off);w('MmSolidTerrain',1,off)
 end
 -- Original actual room: stem X2096/Y32..79, horizontal coral2112../Y64.
 for wx=48,128,16 do for y=32,64,16 do
  if wx==48 or y==64 then
   local cell=q.side==1 and(q.base+wx)or(q.base+112-wx)
   block(cell,y)
  end
 end end
 local start=q.side==1 and(q.base+q.offset)or(q.base+112-q.offset)
 q.start=start
 w('SelectedCharacter',q.char);w('Player_X_Position',start%256);w('Player_PageLoc',start//256)
 w('Player_Y_Position',47);w('Player_Y_HighPos',1);w('Player_State',1)
 local toward=q.side==1 and 20 or -20
 q.vx=q.motion=='stationary'and 0 or(q.motion=='toward'and toward or -toward)
 w('Player_X_Speed',q.vx);w('Player_X_Scroll',1);w('Player_Y_Speed',1)
 w('PlayerStatus',q.power);w('PlayerSize',q.power==0 and 1 or 0);w('CrouchingFlag',0)
 w('PlayerFacingDir',q.side);w('Player_MovingDir',q.side)
 w('Player_CollisionBits',255);w('SideCollisionTimer',0);w('DisableCollisionDet',0)
 w('SwimmingFlag',1);w('AreaType',0);w('MarioWaterActive',1)
 w('GameEngineSubroutine',q.engine);w('JumpspringAnimCtrl',0);w('InjuryTimer',0);w('StarInvincibleTimer',0)
 w('BlockBounceTimer',0);w('RgCrouch',0);w('GuestHurtTicks',0)
 w('MmVX',0x56);w('MmVX',0x34,1);w('MmVX',0x12,2)
 w('MmXFraction',0x9a);w('MmXFraction',0xbc,1);w('MmVY',0x78)
 local camera=q.base-28
 w('ScreenLeft_X_Pos',camera%256);w('ScreenLeft_PageLoc',camera//256)
 w('ScreenRight_X_Pos',(camera+255)%256);w('ScreenRight_PageLoc',(camera+255)//256)
end
local function finishCase()
 local q=current
 local row={index,q.char,q.engine,q.power,q.base,q.side,q.offset,q.motion,q.start,x(),x()-q.start,nativeCalls,wallCalls,positionWrites}
 local projection={x()}
 for _,name in ipairs(fields)do row[#row+1]=r(name);projection[#projection+1]=r(name)end
 out:write(table.concat(row,',')..'\n');out:flush()
 assert(wallCalls>0 and nativeCalls>0,'All native0/8 contacts reach actual native ImpedePlayerMove: case'..index)
 local delta=q.motion=='away'and 0 or(q.side==1 and -1 or 1)
 assert(x()==q.start+delta,'Native contact is bounded to its exact one-pixel correction: case'..index..' dx='..(x()-q.start))
 assert(r('Player_X_Speed')==(q.motion=='away'and q.vx%256 or 0),'Native contact preserves away velocity and stops toward/stationary velocity')
 assert(r('SideCollisionTimer')==(q.motion=='away'and 0 or 16),'Native contact retains its16-frame wall hold')
 assert(r('Player_CollisionBits')==(q.side==1 and 254 or 253),'Native contact clears only the contacted-side bit')
 assert(r('Player_X_Scroll')==1,'Native contact does not execute guest scroll/remainder clearing')
 assert(r('MmVX')==0x56 and r('MmVX',1)==0x34 and r('MmVX',2)==0x12 and r('MmXFraction')==0x9a and r('MmXFraction',1)==0xbc,
  'Native contact preserves unused guest fractions and velocity')
 assert(r('GameEngineSubroutine')==q.engine and r('InjuryTimer')==0,'Collision preserves active/scripted native engine and health')
 local key=table.concat({q.engine,q.power,q.base,q.side,q.offset,q.motion},':')
 if q.char==0 then controls[key]=table.concat(projection,',')
 else assert(controls[key]==table.concat(projection,','),'Luigi post-contact state exactly equals independent Mario0 control')end
 active=false;w('GameEngineSubroutine',8)
 if index==#cases then
  out:close();print('PASS native wall-corner: '..#cases..' actual-parser cases, '..(NATIVE_WALL_CONTROL_ONLY and'independent native Mario0 controls'or'native Mario0/Luigi8 exact collision parity'));emu.stop(0)
 end
end
emu.addMemoryCallback(function()
 if frame<640 or active or r('CurrentBank')%128~=1 then return end
 index=index+1;setup(assert(cases[index]))
 entrySP=emu.getState()['cpu.sp']
 local pc=(emu.read(0x100+(entrySP+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(entrySP+2)%256,emu.memType.nesDebug)+1)%65536
 if not returnPC then
  returnPC=pc
  emu.addMemoryCallback(function()
   if active and emu.getState()['cpu.sp']==entrySP+2 and r('CurrentBank')%128==1 then finishCase()end
  end,emu.callbackType.exec,pc)
 end
 assert(pc==returnPC,'Stable actual native player collision caller')
 active=true
end,emu.callbackType.exec,assert(L.PlayerBGCollision))
emu.addMemoryCallback(function()if active then nativeCalls=nativeCalls+1 end end,emu.callbackType.exec,assert(L.ImpedePlayerMove))
emu.addMemoryCallback(function()if active then wallCalls=wallCalls+1 end end,emu.callbackType.exec,assert(L.SamusStopAtWall))
emu.addMemoryCallback(function()if active then positionWrites=positionWrites+1 end end,emu.callbackType.write,assert(L.Player_X_Position))
emu.addEventCallback(function()emu.setInput({start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;assert(frame<2000,'Bounded native-corner fixture completes')end,emu.eventType.endFrame)
