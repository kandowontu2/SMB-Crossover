CONFIG_UNDER_TEST={["hard"]=true,["enabled"]=false,["optional"]=nil,["nested"]={["values"]={false,true,nil,1,"True","False"}}}
local C=CONFIG_UNDER_TEST
assert(type(C.hard)=='boolean' and C.hard==true,'True survives as a Lua boolean')
assert(type(C.enabled)=='boolean' and C.enabled==false,'False survives as a Lua boolean')
assert(C.optional==nil,'None is a Lua nil')
assert((C.hard and 1 or 0)==1,'Mode predicate selects Hard')
assert((C.enabled and 1 or 0)==0,'False predicate stays false')
assert(C.nested.values[1]==false and C.nested.values[2]==true and C.nested.values[3]==nil and C.nested.values[4]==1,'Nested literal types survive')
assert(C.nested.values[5]=='True' and C.nested.values[6]=='False','String content stays literal')
local f=assert(io.open(OUTPUT..'runtime-proof.json','w'));f:write('{"passed":true,"checks":7,"scope":"Real Lua configuration evaluation; no gameplay or mode coverage claim"}');f:close();emu.stop(0)
