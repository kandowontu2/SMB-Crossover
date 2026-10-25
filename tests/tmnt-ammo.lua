-- Explicit HUD component after cold controller menus. Inventory is arranged;
-- this verifies actual three-digit publication, not natural weapon collection.
local C=assert(TMNT_CFG);local frame=0;local phase=C.mode=='hard'and'options-focus'or'start'
local entered=false;local pending=1;local current=0;local age=0;local checks={}
local values={20,99,100,101,102,0}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function menu()
 if frame<60 or frame%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2
 if row~=2 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end
emu.addEventCallback(function()emu.setInput(entered and{}or menu(),0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if not entered or not pending or bank(L.TnMovement)~=B.TnMovement then return end
 current=pending;pending=nil;age=0
 local value=values[current]
 w('TnEquipment',value>0 and 3 or 0,C.variant)
 w('TnAmmo',value,C.variant)
 w('TnGearSelected',value>0 and 1 or 0)
end,emu.callbackType.exec,L.TnMovement)
emu.addEventCallback(function()
 frame=frame+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant,'Actual requested turtle entered')
  entered=true
 end
 if entered and current>0 then
  age=age+1
  if age==30 then
   local value=values[current];local expected={0x24,0x24,0x24};local actual={}
   if value>0 then expected={value>=100 and 1 or 0x24,(value//10)%10,value%10}end
   for i=1,3 do
    actual[i]=emu.read(0x2030+i,emu.memType.nesPpuDebug)
    assert(actual[i]==expected[i],'Actual three-digit ammo HUD mismatch at value'..value..' column'..i)
   end
   checks[#checks+1]={ammo=value,nametable=actual}
   local p=assert(io.open(TEST_DIR..'ammo-'..value..'.png','wb'));p:write(emu.takeScreenshot());p:close()
   if current==#values then
    local p=assert(io.open(TEST_DIR..'result.json','w'))
    p:write('{"passed":true,"variant":'..C.variant..',"mode":"'..C.mode..'","physical_HUD_values":[20,99,100,101,102,0],"component_inventory_arranged":true}\n');p:close()
    emu.stop(0);return
   end
   pending=current+1
  end
 end
 assert(frame<1800,'TMNT three-digit HUD timed out')
end,emu.eventType.endFrame)
