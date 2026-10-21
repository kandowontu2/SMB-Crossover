-- Explicit source2.02 fixture setup, not a power-on-default or route proof.
-- run_mesen excludes the three controller-only front-end/outline tests.
-- Existing gameplay fixtures choose at frame80 and confirm at120/200.
local frame=0
local selectedSourceRules=false
local function sourceRules()
 if selectedSourceRules or frame~=60 then return end
 selectedSourceRules=true
 if L.CrossoverBehaviorVersion and not ROM_NAME:find('baseline',1,true) then
  emu.write(L.CrossoverBehaviorVersion,1,emu.memType.nesDebug)
  assert(emu.read(L.CrossoverBehaviorVersion,emu.memType.nesDebug)==1,
   'Explicit fixture mode is source2.02; the power-on UI default remains1.0')
 end
end
local rawInput=emu.setInput
emu.setInput=function(buttons,port)
 sourceRules()
 if frame==60 and L.CrossoverMenuState and not ROM_NAME:find('baseline',1,true) then buttons.start=true end
 return rawInput(buttons,port)
end
emu.addEventCallback(function()
 frame=frame+1
 sourceRules()
end,emu.eventType.endFrame)
