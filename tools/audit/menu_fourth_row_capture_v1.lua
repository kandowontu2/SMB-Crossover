-- Cold controller-only menu inspection. Seven bounded screenshots, no RAM writes.
local frame,phase,age,step=0,'title',0,1
local steps={{'down',7,'row2'},{'down',14,'row3'},
 {'down',22,'row4'},{'select',22,'row4-alternate'},
 {'up',15,'back-row3'},{'down',22,'return-row4'}}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local log=assert(io.open(OUTPUT..'menu-observations.csv','w'))
log:write('frame,phase,slot,character,variant,menu,mode\n')
local function shot(tag)
 local p=OUTPUT..'menu-'..tag..'.png';local f=assert(io.open(p,'wb'))
 f:write(emu.takeScreenshot());f:close()
 print('SHOT '..p)
end
emu.addEventCallback(function()
 local b={}
 if phase=='open' then b.start=age<8
 elseif phase=='browse' and step<=#steps then b[steps[step][1]]=age<8 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;age=age+1
 if frame>620 then error('Bounded menu navigation did not complete')end
 if phase=='title' and frame>=100 then
  assert(r('CrossoverMenuState')==0 and r('OperMode')==0,'Cold title')
  phase='open';age=0
 elseif phase=='open' and age>=30 then
  assert(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Start opens real roster')
  shot('row1');phase='browse';age=0
 elseif phase=='browse' and age>=32 then
  local s=steps[step]
  assert(r('CrossoverMenuState')==2 and r('OperMode')==0,'Still real menu')
  assert(r('CrossoverMenuIndex')==s[2],'Requested navigation slot '..s[2])
  shot(s[3]);step=step+1;age=0
  if step>#steps then log:close();print('PASS cold four-row menu navigation and screenshots');emu.stop(0)end
 end
 if frame%8==0 then
  log:write(table.concat({frame,phase,r('CrossoverMenuIndex'),r('SelectedCharacter'),r('MarioVariant'),r('CrossoverMenuState'),r('OperMode')},',')..'\n')
  log:flush()
 end
end,emu.eventType.endFrame)
