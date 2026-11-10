-- Controller-free transport probe. No files or emulated state are written.
local count,stopped=0,false
local function finish(ok,reason)
 if stopped then return end
 stopped=true
 local pin=assert(os.getenv('SMB_STDOUT_ROM_SHA'),'Missing bound ROM hash')
 print('SMB_NATIVE_RECEIPT '..string.format('{"passed":%s,"ROM_SHA256":"%s","frames":%d,"reason":"%s","script_RAM_writes":false}',tostring(ok),pin,count,reason))
 emu.stop(ok and 0 or 1)
end
emu.addEventCallback(function()
 if stopped then return end
 local ok,err=pcall(function()
  count=count+1
  if count>=120 then finish(true,'Native stdout transport and bounded frame callback') end
 end)
 if not ok then finish(false,'Callback failed') end
end,emu.eventType.endFrame)
