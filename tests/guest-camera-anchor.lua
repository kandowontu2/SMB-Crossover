-- Flat-ground camera unit arenas, not level clears. Ordinary held Right drives
-- all characters. A single native side-collision timer models the brief
-- scrolling hold after a wall contact; guests must recover their follow point.
local frame,depth,index,age=0,0,0,0
local chars={0,1,2,3,4,5,6,7,8,9,10,11,12}
local current,lastCamera,normalMax,afterMax
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local log=assert(io.open(OUTPUT..ROM_NAME..'-guest-camera-anchor.csv','w'))
log:write('character,update,x,camera,relative,sideTimer,scroll\n')
emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()depth=depth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()emu.setInput({start=frame==200,right=frame>=550},0)end,emu.eventType.inputPolled)
local function terrain()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do local i=p*208+176+col;w('Block_Buffer_1',0x54,i);w('MmSolidTerrain',1,i)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
end
local function begin(c)
 current=c;age=0;lastCamera=0;normalMax=0;afterMax=0
 terrain()
 w('SelectedCharacter',c);w('PlayerStatus',1);w('PlayerSize',0);w('AreaType',1);w('SwimmingFlag',0)
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('Player_MovingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_Pos_ForScroll',40);w('Player_Rel_XPos',40);w('ScrollLock',0);w('SideCollisionTimer',0)
 w('Player_X_Scroll',0);w('Platform_X_Scroll',0);w('ScrollThirtyTwo',0);w('ScrollAmount',0)
 w('GameEngineSubroutine',8);w('GuestPowerupActive',0);w('TimerControl',0);w('InjuryTimer',0)
 for _,n in ipairs({'MmSliding','MmOnVine','MmUnderwater','MmStepTimer','MmPreviousDir','MmLastXSpeed','SmCrouch','SmBall','RgCrouch','CrouchingFlag','ScPogo','ScAttack','XgWallContact'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
emu.addMemoryCallback(function()
 if frame<550 or depth~=0 then return end
 if current~=nil then
  age=age+1
  local cx,px=camera(),x()
  assert(cx>=lastCamera and cx-lastCamera<=5,'Camera movement is monotonic/bounded, character '..current)
  lastCamera=cx
  local relative=px-cx
  log:write(table.concat({current,age,px,cx,relative,r('SideCollisionTimer'),r('Player_X_Scroll')},',')..'\n');log:flush()
  if age>180 and age<260 then normalMax=math.max(normalMax,relative)end
  if age>320 then afterMax=math.max(afterMax,relative)end
  if age==260 then
   assert(cx>100,'Ordinary movement really starts camera scrolling')
   w('SideCollisionTimer',12)
  end
  if age==400 then
   if current~=0 and current~=8 then
    assert(normalMax<=114,'Guest normal movement stays near Mario follow point: '..current..' / '..normalMax)
    assert(afterMax<=114,'Guest must recover its follow point after a brief side-collision hold: '..current..' / '..afterMax)
   end
   print('PASS camera anchor character '..current..': normal='..normalMax..', after contact='..afterMax)
   current=nil
  end
 end
 if current==nil then
  index=index+1
  if not chars[index]then log:close();print('PASS all11 guest camera anchors recover after transient wall-contact holds; native Mario/Luigi controls retained');emu.stop(0);return end
  begin(chars[index])
 end
 terrain()
end,emu.callbackType.exec,L.NoDecTimers)
emu.addEventCallback(function()frame=frame+1;assert(frame<10000,'Camera matrix completes within its frame bound')end,emu.eventType.endFrame)
