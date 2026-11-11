-- A low flag catch can reach engine state 5 before the next original update.
emu.addMemoryCallback(guarded(function(_,value)
  if not ending or value~=4 or read(0x761)~=0 then return end
  local s=state()
  if s.x>=3158 and s.x<=3161 then
    ending.flag=ending.flag or s
  end
end),emu.callbackType.write,0x0f)
