-- Reference-only capture of native APU writes. AUDIO_FREEZE replaces Rygar's
-- emulated NMI vector with a RAM stub calling only its original $e000 audio
-- driver and bank-3 selector. No on-disk ROM is changed. This extraction
-- fixture is distinct from gameplay/controller verification.
local frame=0
local last={}
local f=assert(io.open(AUDIO_OUTPUT,'w'));f:write('frame,register,value\n')
local dpcm
if AUDIO_DPCM_OUTPUT then
 dpcm=assert(io.open(AUDIO_DPCM_OUTPUT,'w'));dpcm:write('frame,rate,dac,start,length,hex\n')
end
emu.addMemoryCallback(function(address,value)
 if dpcm and address==0x4015 and value&16~=0 and (last[address]or 0)&16==0 then
  local start=0xc000+64*(last[0x4012]or 0)
  local length=16*(last[0x4013]or 0)+1
  local bytes={}
  for i=0,length-1 do bytes[#bytes+1]=string.format('%02x',emu.read(0x8000+(start+i-0x8000)%0x8000,emu.memType.nesDebug))end
  dpcm:write(frame..','..(last[0x4010]or 0)..','..(last[0x4011]or 0)..','..start..','..length..','..table.concat(bytes)..'\n')
 end
 last[address]=value
 if frame>=AUDIO_BEGIN then f:write((frame-AUDIO_BEGIN)..','..(address-0x4000)..','..value..'\n') end
end,emu.callbackType.write,0x4000,0x4015)
emu.addEventCallback(function()
 emu.setInput({start=frame==120 or (AUDIO_NATIVE=='pit' and frame==240)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==AUDIO_BEGIN and AUDIO_BEGIN>0 then
  if AUDIO_FREEZE then
   local state=emu.getState()
   assert(state['cpu.sp']==255,'Freeze only at the native idle loop, outside NMI')
   assert(emu.read(0xfffa,emu.memType.nesDebug)==0xf6 and emu.read(0xfffb,emu.memType.nesDebug)==0xc0 and
    emu.read(0xe000,emu.memType.nesDebug)==0xa2 and emu.read(0xc0ec,emu.memType.nesDebug)==0xbd,'Pinned Rygar driver and NMI layout')
   local stub={0x48,0x8a,0x48,0x98,0x48,0xe6,0x32,0xa2,3,0x20,0xec,0xc0,0x20,0x00,0xe0,0x68,0xa8,0x68,0xaa,0x68,0x40}
   for i,value in ipairs(stub) do emu.write(0xff+i,value,emu.memType.nesDebug) end
   emu.write(131072-6,0x00,emu.memType.nesPrgRom)
   emu.write(131072-5,0x01,emu.memType.nesPrgRom)
   assert(emu.read(0xfffa,emu.memType.nesDebug)==0 and emu.read(0xfffb,emu.memType.nesDebug)==1,'Native audio-only NMI is installed')
   if AUDIO_TRACK then
    -- Start an actual native driver song, with no stale channels from the
    -- opening stage. These are extraction-fixture writes, never port inputs.
    for address=0x740,0x7e3 do emu.write(address,0,emu.memType.nesDebug) end
    for address=0x4000,0x400f do emu.write(address,0,emu.memType.nesDebug);last[address]=0 end
    emu.write(0x4015,0,emu.memType.nesDebug);last[0x4015]=0
    emu.write(0x740,AUDIO_TRACK,emu.memType.nesDebug)
   end
  end
  for address=0x4000,0x400f do f:write('0,'..(address-0x4000)..','..(last[address] or 0)..'\n') end
  f:write('0,21,'..(last[0x4015] or 15)..'\n')
 end
 if frame==AUDIO_END then f:close();if dpcm then dpcm:close()end;print('PASS native APU capture '..AUDIO_OUTPUT);emu.stop(0) end
end,emu.eventType.endFrame)
