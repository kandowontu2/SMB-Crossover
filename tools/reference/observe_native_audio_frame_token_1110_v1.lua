-- Appended to the exact Mini route controller. Passive bus observation only.
do
 local monitor={packed_frames=0,terminal_tokens=0,ordered_music_image_writes=0,
  packed_status_writes=0,apu_writes=0,mmc5_audio_writes=0,ordered_bus_hash=2166136261,
  register_counts={}}
 local pending=nil
 local tokenPC=audioConfig.token_pc

 local function routeAudio()return phase=='fullstage' end
 local function hashByte(v)
  monitor.ordered_bus_hash=((monitor.ordered_bus_hash~v)*16777619)&0xffffffff
 end
 local function noteBus(at,v)
  local key=string.format('%04x',at)
  monitor.register_counts[key]=(monitor.register_counts[key]or 0)+1
  hashByte(at&255);hashByte((at>>8)&255);hashByte(v&255)
 end

 emu.addMemoryCallback(guard(function()
  if not routeAudio()then return end
  local loc=emu.convertAddress(tokenPC)
  if not loc or loc.memType~=emu.memType.nesPrgRom or loc.address~=audioConfig.physical then return end
  check(r('SelectedCharacter')==41 and read(audioConfig.family)==7,'Packed music owner')
  check(pending==nil,'One complete ordered write sequence per packed music frame')
  local token=emu.getState()['cpu.a']
  if token==255 then monitor.terminal_tokens=monitor.terminal_tokens+1;return end
  pending={fields=assert(audioConfig.tokens[token+1],'Valid source ground token'),next=1}
  monitor.packed_frames=monitor.packed_frames+1
 end),emu.callbackType.exec,tokenPC)

 emu.addMemoryCallback(guard(function(at,v)
  if not pending then return end
  local row,i=pending.fields,pending.next
  check(at==audioConfig.image+row[i] and v==row[i+1],'Exact ordered source ground voice byte')
  pending.next=i+2
  monitor.ordered_music_image_writes=monitor.ordered_music_image_writes+1
 end),emu.callbackType.write,audioConfig.image,audioConfig.image+15)

 emu.addMemoryCallback(guard(function(at,v)
  if not routeAudio() or at==0x4014 or at==0x4016 then return end
  noteBus(at,v)
  monitor.apu_writes=monitor.apu_writes+1
  if pending and at==0x4015 then
   check(pending.next==#pending.fields+1 and v&15==15,'Original packed frame status follows all voice writes')
   pending=nil
   monitor.packed_status_writes=monitor.packed_status_writes+1
  end
 end),emu.callbackType.write,0x4000,0x4017)

 emu.addMemoryCallback(guard(function(at,v)
  if not routeAudio() or not (at<=0x5007 or at==0x5010 or at==0x5011 or at==0x5015)then return end
  noteBus(at,v)
  monitor.mmc5_audio_writes=monitor.mmc5_audio_writes+1
 end),emu.callbackType.write,0x5000,0x5015)

 audioAssertFinished=function()
  check(pending==nil and monitor.packed_frames>128,'Actual route exercised packed ground music')
  check(monitor.packed_frames==monitor.packed_status_writes and monitor.ordered_music_image_writes>0,
        'Packed frames published original voice order and hardware status')
  check(monitor.apu_writes>=monitor.packed_status_writes,'Actual APU register bus writes observed')
 end

 local priorFinish=profileFinish
 profileFinish=function()
  priorFinish()
  monitor.ROM_sha256=C.ROM_sha256
  monitor.scope='Ordered register-address/value hash of actual APU/MMC5 writes while the original fullstage controller is active. Packed voice writes and their trailing hardware status are asserted independently. Different controller timing can change this route hash.'
  local f=assert(io.open(OUTPUT..'audio-order.json','w'));f:write(json(monitor)..'\n');f:close()
 end
end
