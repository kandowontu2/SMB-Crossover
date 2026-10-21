-- Independent cold boot: only ordinary fixed controller inputs, no save-state
-- loading and no emulated memory, ROM or register mutations. An optional
-- opaque discovery root is created only after every independent check passes.
local cfg=assert(BRANCH_VERIFY)
local name=cfg.basename or 'winning'
local target=assert(dofile(cfg.out..name..'-target.lua'))
local expected=assert(io.open(cfg.out..name..'-ram.bin','rb')):read('*a')
local inputs={}
for line in io.lines(cfg.out..name..'-inputs.csv')do
 local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
 if p then inputs[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)}end
end
local frame,poll=0,0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 poll=poll+1;local q=assert(inputs[poll],'Fixed winning stream exhausts at exact target')
 assert(q.frame==frame,'Winning stream poll/frame synchronizes from power-on: '..poll)
 local b={};for n,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[n]=(q.mask&bit)~=0 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if poll<target.poll then return end
 assert(poll==target.poll and frame==target.frame,'Cold-boot target has exact frame/poll')
 assert(r('Player_X_Position')+256*r('Player_PageLoc')==target.x and r('Player_Y_Position')==target.y,'Cold-boot target has exact position')
 assert(r('Player_State')==target.state and r('PlayerStatus')==target.power,'Cold-boot target has exact movement and power')
 assert(r('WorldNumber')==target.world and r('LevelNumber')==target.level,'Cold-boot target has exact stage')
 local index=1
 for a=0,0x7ff do assert(emu.read(a,emu.memType.nesDebug)==expected:byte(index),'Cold-boot complete internal RAM agrees at '..a);index=index+1 end
 for a=0x6000,0x7fff do assert(emu.read(a,emu.memType.nesDebug)==expected:byte(index),'Cold-boot complete work RAM agrees at '..a);index=index+1 end
 if cfg.exportRoot then
  local f=assert(io.open(cfg.out..name..'-verified-root.state','wb'))
  f:write(emu.createSavestate());f:close()
 end
 print('PASS independent cold-boot '..name..' branch: exact controller polls, frames, target and all10240RAMbytes; no state loads')
 local f=assert(io.open(cfg.out..(name=='winning'and 'coldboot-verified.json'or name..'-coldboot-verified.json'),'w'));f:write('{"verified":true,"savestate_loads":false,"emulated_writes":false,"ram_bytes_identical":10240}\n');f:close();emu.stop(0)
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
