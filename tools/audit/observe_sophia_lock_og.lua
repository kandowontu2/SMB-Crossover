-- Passive exact-input freeze diagnostic. Never changes emulated state.
local frame,nmis,irqs,stagnant,lastCounter=0,0,0,0,nil
local lastNmiFrame,lastIrqFrame=-1,-1
local firstFault,firstPoison=nil,nil;local ring={};local head,total=0,0
local prefix=assert(SOPHIA_LOCK_OUTPUT)
local trace=assert(io.open(prefix..'state.csv','w'))
trace:write('frame,pc,sp,a,x,y,p,bankA,bankC,gameCounter,nmis,irqs,stagnant,engine,hurtKind,hurtTicks,power,control1,control2\n')
local writes=assert(io.open(prefix..'ppu-writes.csv','w'))
writes:write('frame,pc,address,value,bankA,bankC\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local mutable={}
for _,name in ipairs({'NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC'})do mutable[assert(L[name],name)+1]=true end
mutable[L.FarcallJmpTarget_SMC+2]=true
local smcWrites=assert(io.open(prefix..'invalid-smc-writes.csv','w'))
smcWrites:write('frame,pc,lastExec,opcode,address,expected,value,sp,bankA,bankC\n')
local lastExec=0;local minimumSP=255;local minimumStackAddress=512
emu.addMemoryCallback(function(address,value)
 if frame<300 then return end
 if address<minimumStackAddress and address>=L.__SMCCODE_RUN__+L.__SMCCODE_SIZE__ then
  local s=emu.getState()
  if address==0x100+s['cpu.sp'] then minimumStackAddress=address;minimumSP=math.min(minimumSP,s['cpu.sp']-1)end
 end
 if address<L.__SMCCODE_RUN__ or address>=L.__SMCCODE_RUN__+L.__SMCCODE_SIZE__ then return end
 if mutable[address]then return end
 local expected=SOPHIA_SMC_ORIGINAL[address-L.__SMCCODE_RUN__+1]
 if value==expected then return end
 local ok,err=pcall(function()
  local s=emu.getState();minimumSP=math.min(minimumSP,s['cpu.sp'])
  local row={frame,s['cpu.pc'],lastExec,0,address,expected or -1,value,s['cpu.sp'],0,0}
  for i=1,#row do row[i]=tostring(row[i])end
  smcWrites:write(table.concat(row,',')..'\n');smcWrites:flush()
  if not firstPoison then firstPoison={frame=frame,pc=s['cpu.pc'],address=address,sp=s['cpu.sp']}end
 end)
 if not ok then emu.log('SMC observer error: '..tostring(err))end
end,emu.callbackType.write,0x100,0x1ff)
local function screenshot(name)local f=assert(io.open(prefix..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function snapshot(pc,s)
 local f=assert(io.open(prefix..'first-invalid-execution.csv','w'))
 f:write('frame,pc,opcode,sp,a,x,y,p,bankA,bankC\n')
 for i=math.max(1,total-1023),total do
  local row=ring[(i-1)%1024+1]
  if row then f:write(table.concat(row,',')..'\n')end
 end
 f:close()
 local out=assert(io.open(prefix..'first-fault-ram.bin','wb'))
 for a=0,0x7ff do out:write(string.char(emu.read(a,emu.memType.nesDebug)))end
 for a=0x5c00,0x7fff do out:write(string.char(emu.read(a,emu.memType.nesDebug)))end
 out:close()
 firstFault={pc=pc,sp=s['cpu.sp'],frame=frame}
end
local function finish()
  trace:close();writes:close();smcWrites:close()
  if SOPHIA_EXPECT_REPAIRED then
   assert(stagnant<3 and frame-lastNmiFrame<3 and frame-lastIrqFrame<3,'Repaired endpoint has recent game, NMI and IRQ updates after the real transition')
   assert(not firstFault and not firstPoison,'No execution outside declared code or immutable SMC overwrite')
   assert(minimumSP>=0x7a,'Hardware stack remains above the last live SMC byte')
  else
   assert(stagnant>=10 and firstFault and firstPoison,'Recorded scene actually stops game updates after SMC corruption')
  end
  local out=assert(io.open(prefix..'observed.json','w'))
  out:write(string.format('{"repaired":%s,"frames":%d,"stagnant_frames":%d,"nmis":%d,"irqs":%d,"first_invalid_pc":%d,"first_invalid_frame":%d,"first_poison_frame":%d,"first_poison_pc":%d,"first_poison_address":%d,"observed_minimum_SP":%d,"minimum_stack_write_address":%d,"read_only":true}',tostring(SOPHIA_EXPECT_REPAIRED or false),frame,stagnant,nmis,irqs,firstFault and firstFault.pc or -1,firstFault and firstFault.frame or -1,firstPoison and firstPoison.frame or -1,firstPoison and firstPoison.pc or -1,firstPoison and firstPoison.address or -1,minimumSP,minimumStackAddress));out:close()
end
if SOPHIA_GUARD_UNTIL_CLEAR then
 local rawStop=emu.stop
 emu.stop=function(code)if code==0 then finish()end;rawStop(code)end
end
emu.addMemoryCallback(function()nmis=nmis+1;lastNmiFrame=frame end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()irqs=irqs+1;lastIrqFrame=frame end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function(address,value)
 if frame<2980 or frame>3010 then return end
 local s=emu.getState()
 writes:write(table.concat({frame,s['cpu.pc'],address,value,bank(0xa000),bank(0xc000)},',')..'\n')
end,emu.callbackType.write,0x2000,0x2007)
local function execution(pc)
 if SOPHIA_EXPECT_REPAIRED then
  if pc>=L.__SMCCODE_RUN__ and pc<L.__SMCCODE_RUN__+L.__SMCCODE_SIZE__ then return end
  if not firstFault then snapshot(pc,emu.getState())end
  return
 end
 if frame<2980 or frame>3010 or firstFault then return end
 local s=emu.getState();total=total+1
 lastExec=pc;minimumSP=math.min(minimumSP,s['cpu.sp'])
 ring[(total-1)%1024+1]={frame,pc,emu.read(pc,emu.memType.nesDebug),s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or 0,bank(0xa000),bank(0xc000)}
 if pc<0x8000 and not(pc>=L.__SMCCODE_RUN__ and pc<L.__SMCCODE_RUN__+L.__SMCCODE_SIZE__)then snapshot(pc,s)end
end
emu.addMemoryCallback(execution,emu.callbackType.exec,0,SOPHIA_EXPECT_REPAIRED and 0x7fff or 0xffff)
emu.addEventCallback(function()
 frame=frame+1
 if frame<2900 then return end
 local s=emu.getState();local counter=r('FrameCounter')
 stagnant=counter==lastCounter and stagnant+1 or 0;lastCounter=counter
 trace:write(table.concat({frame,s['cpu.pc'],s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or 0,bank(0xa000),bank(0xc000),counter,nmis,irqs,stagnant,r('GameEngineSubroutine'),r('GuestHurtKind'),r('GuestHurtTicks'),r('PlayerStatus'),r('Mirror_PPUCTRL'),r('Mirror_PPUMASK')},',')..'\n')
 if frame>=2992 and frame<=3008 then screenshot(string.format('scene-%06d',frame))end
 if frame==3020 and not SOPHIA_GUARD_UNTIL_CLEAR then
  finish()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
