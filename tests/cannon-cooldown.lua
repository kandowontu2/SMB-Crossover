-- Explicit scoped native-call arenas. No actor, CPU, ROM or hardware edits.
-- Restore the borrowed area/character/timer values at the actual caller return.
local frame,index,depth=0,0,0
local cases={}
for c=0,12 do for v=0,(c==3 and 1 or 0)do for mode=0,1 do for area=0,3 do
 cases[#cases+1]={character=c,variant=v,mode=mode,area=area}
end end end end
local current
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0)end,emu.callbackType.exec,assert(pc))end
local out=assert(io.open(OUTPUT..ROM_NAME..'-cannon-cooldown.csv','w'))
out:write('case,character,variant,mode,area,timer0,timer1,timer2,timer3,timer4,timer5\n')
emu.addMemoryCallback(function()
 if frame<600 or depth~=0 or r('CurrentBank')%128~=0 then return end
 assert(not current,'Previous native whirlpool call has returned')
 index=index+1
 local q=cases[index]
 if not q then out:close();print('PASS '..#cases..' native cannon/whirlpool alias arenas: all14 identities, both modes, all4 area types, all6 timer bytes; dry cooldown retained and water reset preserved');emu.stop(0);return end
 current=q;q.old={};q.timer={};q.page={}
 for _,n in ipairs({'AreaType','SelectedCharacter','BillVariant','CrossoverBehaviorVersion','TimerControl'})do q.old[n]=r(n)end
 for i=0,5 do q.timer[i]=r('Cannon_Timer',i);q.page[i]=r('Cannon_PageLoc',i);w('Cannon_Timer',14-i,i);w('Cannon_PageLoc',0,i)end
 w('AreaType',q.area);w('SelectedCharacter',q.character);w('BillVariant',q.variant);w('CrossoverBehaviorVersion',q.mode);w('TimerControl',0)
end,emu.callbackType.exec,L.ProcessWhirlpools)
emu.addMemoryCallback(function()
 if not current or depth~=0 or r('CurrentBank')%128~=0 then return end
 local q=current;local values={index,q.character,q.variant,q.mode,q.area}
 for i=0,5 do
  local expected=q.area==0 and i==0 and 0 or 14-i
  local actual=r('Cannon_Timer',i)
  assert(actual==expected,'Cannon cooldown byte'..i..' survives dry whirlpool dispatch: character'..q.character..' area'..q.area..' actual'..actual..' expected'..expected)
  values[#values+1]=actual
 end
 out:write(table.concat(values,',')..'\n')
 for n,v in pairs(q.old)do w(n,v)end
 for i=0,5 do w('Cannon_Timer',q.timer[i],i);w('Cannon_PageLoc',q.page[i],i)end
 current=nil
end,emu.callbackType.exec,L.FlagpoleRoutine)
emu.addEventCallback(function()emu.setInput({start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;assert(frame<1200,'Bounded native alias regression')end,emu.eventType.endFrame)
