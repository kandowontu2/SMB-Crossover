-- Fixed-input replay observer only. Addresses come from the tested ROM's labels.
local frame, seen = 0, false
local function r(name) return emu.read(assert(L[name], name), emu.memType.nesDebug) end
emu.addEventCallback(function()
  frame = frame + 1
  if frame > 540 and r('OperMode') == 1 and r('OperMode_Task') == 3 and r('GameEngineSubroutine') == 8 then
    assert(r('SelectedCharacter') == 2 and r('CrossoverBehaviorVersion') == 0
      and r('MarioVariant') == 0 and r('PlayerOutlinesOff') == 1, 'Actual Easy Samus/variant0/shadowsOff identity')
    if not seen then
      local f = assert(io.open(ROSTER_CONFIG.out .. 'ordinary-identity.json', 'w'))
      f:write('{"selected":2,"behavior":0,"variant":0,"outlinesOff":1,"observed":true,"frame":' .. frame .. '}')
      f:close()
      seen = true
    end
  end
end, emu.eventType.endFrame)
return function() return {} end
