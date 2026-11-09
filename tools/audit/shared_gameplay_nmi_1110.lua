-- Attached to the natural cadence replay. Samples only missed active NMIs.
local profilePhase, lastNmi, lastMain, samples = nil, nil, nil, {}
local function cycle() return emu.getState()['cpu.cycleCount'] end
observe(0x82d9,{0xa9,0xff,0x8d},function()
 if profilePhase then lastMain=cycle() end
end)
emu.addMemoryCallback(function()
 if not profilePhase or not active() then return end
 local at=emu.convertAddress(0xe33c)
 if not at or at.memType~=emu.memType.nesPrgRom then return end
 local bank=at.address//8192
 if bank~=127 and bank~=119 and bank~=120 and bank~=125 then return end
 assert(read(0xe33c)==0x48 and read(0xe33d)==0x8a and read(0xe33e)==0x48)
 local s=emu.getState()
 local now, sp=s['cpu.cycleCount'],s['cpu.sp']
 if read(0x139)<128 then lastNmi=now;return end
 assert(#samples<64,'Missed deadline sample bound')
 local pc=read(0x100+((sp+2)&255))+256*read(0x100+((sp+3)&255))
 local physical=emu.convertAddress(pc)
 local interrupted=physical and physical.memType==emu.memType.nesPrgRom and physical.address//8192 or -1
 samples[#samples+1]=string.format('{"phase":%q,"frame":%d,"x":%d,"pc":%d,"bank":%d,'..
  '"cycles_since_normal_nmi":%d,"cycles_since_main_entry":%d,"stack_depth":%d}',
  profilePhase,frame,x(),pc,interrupted,lastNmi and now-lastNmi or -1,
  lastMain and now-lastMain or -1,255-sp)
end,emu.callbackType.exec,0xe33c)

local function writeDeadlines(expected)
 assert(#samples==expected,'All missed NMIs in the measured windows were captured')
 local file=assert(io.open(OUTPUT..'deadlines.json','w'))
 file:write('['..table.concat(samples,',')..']\n')
 file:close()
end
