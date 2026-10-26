
local names={"MmRenderPose","MmSliding","MmWalkFrame","MmStepTimer","GuestHurtTicks","GuestInvulTicks","GuestHurtVisible","InjuryTimer","PlayerFacingDir","Player_Rel_XPos","Player_Y_Position","Player_Y_HighPos","PlayerStatus","PlayerOutlinesOff","ObjectMetasprite","FrameCounter","GuestPowerupActive"}
local addresses={26771,26800,26770,26834,28445,28446,28448,1947,1342,1393,189,164,1883,32440,1761,14,27645}
local out="C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/root-megaman-lowbody-probe-v1/native/"
local stateFile=assert(io.open(out..'visibility.csv','w'))
local ctrl,mask,lastDmaCycle=0,0,-1
local function hex(at,count,kind)
 local t={};for i=0,count-1 do t[#t+1]=string.format('%02x',emu.read(at+i,kind))end
 return table.concat(t)
end
local function ram()
 local t={};for _,at in ipairs(addresses)do t[#t+1]=emu.read(at,emu.memType.nesDebug)end
 return table.concat(t,':')
end
local lastDmaRam=''
emu.addMemoryCallback(function(a,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(a,v)mask=v end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()
 lastDmaCycle=emu.getState()['cpu.cycleCount'];lastDmaRam=ram()
end,emu.callbackType.write,0x4014)
stateFile:write('ppuFrame,cpuCycle,ctrl,mask,lastDmaCycle,ram,lastDmaRam,chrBanks,hardwareOam,palette\n')
emu.addEventCallback(function()
 local s=emu.getState();local frame=s['ppu.frameCount']
 if frame<500 or frame>3000 then return end
 local banks={};for i=0,11 do banks[#banks+1]=assert(s['mapper.chrBanks'..i])end
 stateFile:write(table.concat({frame,s['cpu.cycleCount'],ctrl,mask,lastDmaCycle,ram(),lastDmaRam,
  table.concat(banks,':'),hex(0,256,emu.memType.nesSpriteRam),hex(0,32,emu.memType.nesPaletteRam)},',')..'\n')
 stateFile:flush()
end,emu.eventType.endFrame)
local oldStop=emu.stop
emu.stop=function(code)stateFile:close();oldStop(code)end
