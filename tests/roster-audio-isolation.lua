local frame,checks=0,0
local character=assert(AUDIO_CHARACTER)
local before
local fields={'Player_State','GameEngineSubroutine','CurrentPlayer','StarFlagTaskControl'}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function()
 if frame<550 then return end
 -- Distinct nonzero sentinels expose writes even with no active enemy in
 -- these slots. Castlevania legitimately borrows $22 and must restore it.
 for i=0,5 do w('Enemy_State',0x20+i,i) end
 before={}
 for _,n in ipairs(fields) do before[n]=r(n) end
 for i=0,5 do before['enemy'..i]=r('Enemy_State',i) end
end,emu.callbackType.exec,L.RosterAudioUpdate)
emu.addMemoryCallback(function()
 if not before then return end
 for _,n in ipairs(fields) do assert(r(n)==before[n],'Character '..character..' audio preserves '..n) end
 for i=0,5 do assert(r('Enemy_State',i)==before['enemy'..i],'Character '..character..' audio preserves enemy slot '..i) end
 checks=checks+1;before=nil
end,emu.callbackType.exec,L.ExitNMI)
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*character and (frame-80)%20==0,start=frame==200,b=frame>=550 and frame%16<8},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==650 then
  assert(checks>=95,'Audio isolation exercised consecutive NMIs')
  print('PASS character '..character..' audio preserves live player, enemy, and end-of-level state through '..checks..' NMIs');emu.stop(0)
 end
end,emu.eventType.endFrame)
