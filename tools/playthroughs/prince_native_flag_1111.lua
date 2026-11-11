-- A low flag catch can reach engine state 5 before the next original update.
emu.addMemoryCallback(guarded(function(_,value)
  if not ending or value~=4 or read(0x761)~=0 then return end
  local s=state()
  local contact=read(0x07)
  if s.x>=3158 and s.x<=3171 and contact>=6 and contact<=9 then
    s.native_flag_write=value
    s.flag_contact=contact
    ending.flag=ending.flag or s
  end
end),emu.callbackType.write,0x0f)
