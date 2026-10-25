local inheritedAbilityAssert=assert
local function failureJson(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..failureJson(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
function assert(ok,message,...)
 if not ok then
  local state=emu.getState();local p=emu.convertAddress(state['cpu.pc'])
  local f=io.open(OUTPUT..'first-failure.json','w')
  if f then f:write(failureJson({message=tostring(message),phase=FINAL_ABILITY_PHASE,pc=state['cpu.pc'],bank=p and p.address//8192 or-1,sp=state['cpu.sp'],a=state['cpu.a'],x=state['cpu.x'],y=state['cpu.y']}));f:close()end
  local f=io.open(OUTPUT..'first-failure.argb','wb');if f then for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end
 end
 return inheritedAbilityAssert(ok,message,...)
end
