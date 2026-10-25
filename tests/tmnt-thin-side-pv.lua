-- Cold Hard Donatello, then a declared native recoil/thin-brick component.
local C=assert(THIN_CFG);local frame,age,entered=0,0,false
local phase='options-focus';local rows={};local lastX;local maxStep=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function menu()
 if frame<60 or frame%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then phase='back';return{a=true}end
  phase='back'
 end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');if ix<12 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=3 then return{select=true}end
 return{a=true}
end
emu.addEventCallback(function()emu.setInput(entered and{right=true}or menu(),0)end,emu.eventType.inputPolled)
local log=assert(io.open(TEST_DIR..'positions.csv','w'));log:write('frame,x,y,vx,vy,state,seq,hurt\n')
emu.addEventCallback(function()
 frame=frame+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==19 and r('TnVariant')==3 and r('CrossoverBehaviorVersion')==1,'Actual requested Hard turtle')
  entered=true
  -- Keep native first-screen floor/provenance; only one explicitly declared
  -- floating solid is added to the ordinary native terrain buffer.
  w('Block_Buffer_1',0xc0,96+8)
  for i=0,5 do w('Enemy_Flag',0,i)end
  for _,q in ipairs({{'Player_X_Position',146},{'Player_PageLoc',0},{'Player_Y_Position',120},{'Player_Y_HighPos',1},
   {'Player_State',2},{'Player_X_Speed',224},{'Player_Y_Speed',0},{'TnVXHi',254},{'TnVXLo',0},{'TnVYHi',0},{'TnVYLo',0},
   {'TnXFraction',0},{'TnYFraction',0},{'TnLastVx',224},{'TnLastVy',0},{'TnSeq',133},{'TnPhase',0},{'TnPose',16},
   {'TnNativeState',7},{'TnNativeFlags',0},{'TnHurt',120},{'TnHurtMove',20},{'TnAttack',0},{'TnThrow',0},{'TimerControl',0},
   {'MmDeathFlag',0},{'ScrollLock',1},{'ScreenLeft_X_Pos',0},{'ScreenLeft_PageLoc',0}})do w(q[1],q[2])end
  lastX=146
 elseif entered then
  age=age+1;local x=r('Player_X_Position')+256*r('Player_PageLoc');maxStep=math.max(maxStep,math.abs(x-lastX));lastX=x
  log:write(table.concat({frame,x,r('Player_Y_Position'),r('Player_X_Speed'),r('Player_Y_Speed'),r('Player_State'),r('TnSeq'),r('TnHurt')},',')..'\n')
  if age<=40 then local f=assert(io.open(TEST_DIR..string.format('frame-%03d.png',age),'wb'));f:write(emu.takeScreenshot());f:close()end
  if age==60 then
   assert((maxStep>8)==C.expect_bad,'The unchanged movement bound must distinguish the retained failure and repair')
   log:close();local f=assert(io.open(TEST_DIR..'result.json','w'));f:write('{"passed":true,"max_world_step":'..maxStep..',"expect_bad":'..tostring(C.expect_bad)..',"arranged_component":true}\n');f:close();emu.stop(0)
  end
 end
 assert(frame<1200,'Thin-side component is bounded')
end,emu.eventType.endFrame)
