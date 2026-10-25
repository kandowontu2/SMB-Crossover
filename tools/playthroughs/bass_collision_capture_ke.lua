-- Passive capture of controller-attained Bass coral contacts. Flat RAM dumps
-- are observations; no ROM/RAM/register writes or save-state loads are used.
local cfg=assert(ROSTER_CONFIG)
local frame,number,active,closed=0,0,nil,false
local bankSelect,interruptDepth=0,0
local returns={}
local f=assert(io.open(cfg.out..'bass-collision-calls.csv','w'))
f:write('frame,call,event,cycle,pc,bank,a,x,y,p,sp,playerX,playerY,yHigh,state,speed,side,row,tile,xNibble,probeX,probeOffset,address,value,bank8000,bankA000,bankC000,bankE000,mapperSelect,interruptDepth\n')
local writes=assert(io.open(cfg.out..'bass-collision-writes.bin','wb'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function raw(a)return emu.read(a,emu.memType.nesDebug)end
local function wanted()return not closed and frame+1>=26600 and frame+1<=26884 and r('WorldNumber')==1 and r('LevelNumber')==1 end
local function state()return emu.getState()end
local function physical(pc)
 local a=emu.convertAddress(pc)
 return a and a.memType==emu.memType.nesPrgRom and a.address//8192 or -1
end
local function dump(name)
 local data={}
 for a=0,0x7ff do data[#data+1]=string.char(raw(a))end
 for a=0x6000,0x7fff do data[#data+1]=string.char(raw(a))end
 local out=assert(io.open(cfg.out..name..'.bin','wb'));out:write(table.concat(data));out:close()
end
local function record(event,address,value)
 local s=state()
 f:write(table.concat({frame+1,active or 0,event,s['cpu.cycleCount']or s['cpu.cycle'],s['cpu.pc'],physical(s['cpu.pc']),s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or -1,s['cpu.sp'],
  r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_X_Speed'),r('R0'),r('R2'),r('R3'),r('R4'),r('R5'),r('Local_eb'),address or -1,value or -1,
  physical(0x8000),physical(0xa000),physical(0xc000),physical(0xe000),bankSelect,interruptDepth},',')..'\n');f:flush()
end
emu.addMemoryCallback(function(_,v)bankSelect=v end,emu.callbackType.write,0x8000)
for _,name in ipairs({'NonMaskableInterrupt','IrqScrollSplit'})do
 emu.addMemoryCallback(function()
  if physical(L[name])==B[name]then interruptDepth=interruptDepth+1;if active and wanted()then record('interrupt-entry-'..name)end end
 end,emu.callbackType.exec,L[name])
 if L[name..'_RTI']then
  emu.addMemoryCallback(function()
   if physical(L[name..'_RTI'])==B[name]then if active and wanted()then record('interrupt-return-'..name)end;interruptDepth=interruptDepth-1;assert(interruptDepth>=0)end
  end,emu.callbackType.exec,L[name..'_RTI'])
 end
end
emu.addMemoryCallback(function()
 if not wanted()or physical(L.PlayerBGCollision)~=B.PlayerBGCollision then return end
 assert(not active,'No nested player terrain call')
 number=number+1;active=number;record('entry');dump('bg-'..number..'-entry-ram')
 local sp=state()['cpu.sp'];local target=raw(0x100+((sp+1)&255))+256*raw(0x100+((sp+2)&255))+1
 target=target&0xffff
 local targetBank=physical(target)
 if not returns[target]then
  returns[target]=true
  emu.addMemoryCallback(function()
   if active and wanted()and state()['cpu.sp']==((sp+2)&255)and physical(target)==targetBank then
    record('return');dump('bg-'..active..'-return-ram');active=nil
   end
  end,emu.callbackType.exec,target)
 end
end,emu.callbackType.exec,L.PlayerBGCollision)
emu.addMemoryCallback(function()
 if wanted()and physical(L.SamusStopAtWallBanked)==B.SamusStopAtWallBanked then record('wall-entry')end
end,emu.callbackType.exec,L.SamusStopAtWallBanked)
for _,name in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed'})do
 emu.addMemoryCallback(function(a,v)if wanted()then record('write-'..name,a,v)end end,emu.callbackType.write,L[name])
end
emu.addEventCallback(function()
 frame=frame+1
 if frame==26599 then
  -- Add the expensive complete writer only for the bounded contact window.
  emu.addMemoryCallback(function(a,v)
   if active and wanted()then writes:write(string.pack('<I4I2I1I1I2',active,a,v,interruptDepth,state()['cpu.pc']))end
  end,emu.callbackType.write,0,0xffff)
 end
 if frame==26890 then
  assert(not active,'Completed final observed terrain call')
  f:close();writes:close();closed=true
  local out=assert(io.open(cfg.out..'bass-collision-capture.json','w'))
  out:write('{"calls":'..number..',"first_frame":26600,"last_frame":26884,"flat_RAM_bytes_per_capture":10240,"emulated_writes":false,"savestate_loads":false}\n');out:close()
 end
end,emu.eventType.endFrame)
return function()return{}end
