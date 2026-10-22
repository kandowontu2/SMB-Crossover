-- Explicit source2.02 fixture setup, not a power-on-default or route proof.
-- run_mesen excludes the three controller-only front-end/outline tests.
-- Existing gameplay fixtures choose at frame80 and confirm at120/200.
local frame=0
local selectedSourceRules=false
local fixtureMode=1
-- Fixtures whose oracle is the original linked source (EASY) opt in before
-- frame60; every other fixture keeps the explicit source2.02 (HARD) setup.
function SelectEasyRules() fixtureMode=0 end
local function sourceRules()
 if selectedSourceRules or frame~=60 then return end
 selectedSourceRules=true
 if L.CrossoverBehaviorVersion and not ROM_NAME:find('baseline',1,true) then
  emu.write(L.CrossoverBehaviorVersion,fixtureMode,emu.memType.nesDebug)
  assert(emu.read(L.CrossoverBehaviorVersion,emu.memType.nesDebug)==fixtureMode,
   'Explicit fixture mode is set; the power-on UI default remains EASY')
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
