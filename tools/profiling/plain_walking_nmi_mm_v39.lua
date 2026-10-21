-- Read-only extension of the same authored crowd arena. Observe the actual
-- C000 audio wrapper as well as A000 driver banks and fixed callers.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_nmi_v37.lua','r'))
local source=f:read('*a');f:close()
local function replace(old,new)
 local at=assert(source:find(old,1,true),'observer anchor: '..old)
 assert(not source:find(old,at+#old,true),'single observer anchor')
 source=source:sub(1,at-1)..new..source:sub(at+#old)
end
replace('local physicalA,physicalSelect=nil,nil','local physicalA,physicalC,physicalSelect=nil,nil,nil')
replace('emu.addMemoryCallback(function(_,value)physicalA=value%128 end,emu.callbackType.write,0x5115)',
 'emu.addMemoryCallback(function(_,value)physicalA=value%128 end,emu.callbackType.write,0x5115)\n emu.addMemoryCallback(function(_,value)physicalC=value%128 end,emu.callbackType.write,0x5116)')
replace('if physicalSelect==7 then physicalA=value%128 end',
 'if physicalSelect==7 then physicalA=value%128 elseif physicalSelect==6 then physicalC=value%128 end')
replace("{'AudioUpdate','SamusAudioUpdate',", "{'AudioUpdate','MegaManAudioUpdate','MegaManAudioNativeUpdate','SamusAudioUpdate',")
replace('local bank=nil',"local bank,window=nil,'A'")
replace("else assert(address>=0xe000,name..' is fixed')end",[=[elseif address>=0xc000 and address<0xe000 then
   window='C'
   local segmentStart,offset=debug:match('seg%s+id='..segment..',name="[^"]+",start=(0x%x+),[^\n]*ooffs=(%d+)')
   assert(tonumber(segmentStart)==0xc000,name..' C000 bank')
   bank=(tonumber(offset)-16)//8192
  else assert(address>=0xe000,name..' is fixed')end]=])
replace('(bank and physicalA~=bank)',"(bank and(window=='C'and physicalC or physicalA)~=bank)")
replace('bank=bank,depth=depth', 'bank=bank,window=window,depth=depth')
replace('(not a.bank or physicalA==a.bank)',"(not a.bank or(a.window=='C'and physicalC or physicalA)==a.bank)")
assert(load(source,'@nmi-mm-v39','t',_ENV))()
