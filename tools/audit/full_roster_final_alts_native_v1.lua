-- Cold native presentation/independent Select-state check for the final additions.
local frame,phase,age,at,shots=0,'title',0,1,0
local steps={
 {'down',8,12}, {'right',9,9}, {'select',9,9,'roll'},
 {'select',9,0,'quick-man'}, {'right',10,10},
 {'select',10,0,'shinobi'}, {'select',10,0,'thomas'},
 {'up',2,2}, {'down',10,0}, {'left',9,0},
 {'select',9,9}, {'right',10,0}, {'select',10,10},
 {'down',18,19}, {'down',26,0}, {'right',27,0},
 {'right',28,0}, {'right',29,0}, {'right',30,0}, {'right',31,0,'arthur'},
 {'start',31,0}
}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function flags()return emu.read(0x5fe5,emu.memType.nesDebug)end
emu.addEventCallback(function()
 local b={}
 if phase=='open'and age<6 then b.start=true
 elseif phase=='browse'and age<4 then b[steps[at][1]]=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;age=age+1;assert(frame<1000,'Bounded final-alternate check')
 if phase=='title'and frame==100 then phase='open';age=0
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2);phase='browse';age=0
 elseif phase=='browse'and age>=24 then
  local s=steps[at]
  assert(r('CrossoverMenuState')==2 and r('OperMode')==0,'Actual selector remains active')
  assert(r('CrossoverMenuIndex')==s[2]and r('SelectedCharacter')==s[3],'Correct family/raw owner')
  if at==7 or at==9 or at==10 then assert(flags()&96==96,'Independent Thomas/Quick choices persist')end
  if at==11 then assert(flags()&96==64,'Cycling Bass preserves Thomas')end
  if at==13 then assert(flags()&96==0,'Both alternate cycles return to base')end
  if s[4]then
   shots=shots+1;assert(shots<=8)
   local f=assert(io.open(OUTPUT..s[4]..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  at=at+1;age=0
  if at>#steps then
   local f=assert(io.open(OUTPUT..'result.json','w'));f:write(string.format('{"passed":true,"frames":%d,"screenshots":%d,"independent_select_states":true,"arthur_start_blocked":true}\n',frame,shots));f:close()
   print('PASS authentic Arthur/QuickMan/Thomas native menu presentation and independent Select cycles')
   emu.stop(0)
  end
 end
end,emu.eventType.endFrame)
