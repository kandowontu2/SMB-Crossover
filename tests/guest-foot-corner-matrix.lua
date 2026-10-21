-- Explicit recovery matrix. Scrooge drives the room; each guest profile is
-- selected only during the shared foot-contact selector/wall clamp. This
-- isolates the new helper without pretending an in-game character switch.
local frame,index=0,0
local current,startX,lastX,maxStep,contacts,override,wallSp,wallReturn
local cases={}
for _,char in ipairs({1,2,3,4,5,6,7,9,10,11,12})do
 for _,boundary in ipairs({128,256,512,768})do
  for _,side in ipairs({'left','right'})do cases[#cases+1]={char=char,boundary=boundary,side=side}end
 end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local out=assert(io.open(OUTPUT..ROM_NAME..'-guest-foot-corner-matrix.csv','w'))
out:write('case,guest,boundary,side,startX,endX,maxFrameStep,contacts\n')
local function begin(q)
 current=q
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for row=6,12 do for col=0,15 do
  local off=page*208+row*16+col;w('Block_Buffer_1',0x54,off);w('MmSolidTerrain',1,off)
 end end end
 local left=q.side=='left' and q.boundary or q.boundary-64
 for wx=left,left+48,16 do for row=2,5 do
  local off=(wx//256)%2*208+row*16+(wx%256)//16
  w('Block_Buffer_1',0x54,off);w('MmSolidTerrain',1,off)
 end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 startX=q.side=='left' and q.boundary-1 or q.boundary-15
 lastX=startX;maxStep=0;contacts=0
 w('SelectedCharacter',12);w('Player_X_Position',startX%256);w('Player_PageLoc',startX//256)
 w('Player_Y_Position',42);w('Player_Y_HighPos',1);w('Player_State',1)
 w('Player_X_Speed',0);w('Player_Y_Speed',1);w('Player_MovingDir',q.side=='left' and 2 or 1);w('PlayerFacingDir',q.side=='left' and 2 or 1)
 local camera=math.max(0,q.boundary-128)
 w('ScreenLeft_X_Pos',camera%256);w('ScreenLeft_PageLoc',camera//256)
 w('ScreenRight_X_Pos',(camera+255)%256);w('ScreenRight_PageLoc',(camera+255)//256)
 w('PlayerStatus',0);w('TimerControl',0);w('InjuryTimer',0);w('ScPogo',0);w('ScAttack',0)
 w('ScPrevious',0);w('RgPreviousButtons',0);w('RgCrouch',0);w('CrouchingFlag',0);w('XgRise',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',1,2)
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
emu.addMemoryCallback(function()
 if not current then return end
 contacts=contacts+1;override=true;w('SelectedCharacter',current.char)
end,emu.callbackType.exec,assert(L.GuestFootContactSide))
emu.addMemoryCallback(function()
 if not current or not override then return end
 assert(r('R0')==(current.side=='left' and 1 or 2),'Actual left/right corner chooses its local contacted edge for guest '..current.char)
 wallSp=emu.getState()['cpu.sp']
 local pc=(emu.read(0x100+(wallSp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(wallSp+2)%256,emu.memType.nesDebug)+1)%65536
 if not wallReturn then
  wallReturn=pc
  emu.addMemoryCallback(function()
   if not current or not override or emu.getState()['cpu.sp']~=wallSp+2 then return end
   w('SelectedCharacter',12);override=false
  end,emu.callbackType.exec,pc)
 end
 assert(pc==wallReturn,'Stable shared wall-clamp caller')
end,emu.callbackType.exec,L.SamusStopAtWall)
emu.addEventCallback(function()emu.setInput({down=frame==80,right=frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=640 and current then
  local now=x();maxStep=math.max(maxStep,math.abs(now-lastX));lastX=now
 end
 if frame>=640 and(frame-640)%20==0 then
  if current then
   assert(not override,'Temporary guest profile returns before the next frame')
   assert(contacts>0,'Actual deep foot-contact path exercised')
   assert(maxStep<=15,'A local separation must not repeat16px wall traversals')
   if current.side=='left'then assert(x()<=current.boundary-1,'Left entry remains outside the full ledge')
   else assert(x()>=current.boundary-1,'Mirrored right entry remains outside the full ledge')end
   assert(math.abs(x()-startX)<=15,'A stationary corner cannot travel across a protected64px row')
   assert(r('GameEngineSubroutine')==8,'Recovery remains playable')
   out:write(table.concat({index,current.char,current.boundary,current.side,startX,x(),maxStep,contacts},',')..'\n');out:flush()
  end
  index=index+1
  if not cases[index]then
   current=nil;out:close();print('PASS guest foot-corner matrix: '..#cases..' real mirrored/page-seam recoveries across11guest contact profiles');emu.stop(0);return
  end
  begin(cases[index])
 end
end,emu.eventType.endFrame)
