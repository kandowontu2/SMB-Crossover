-- Current-hash bank/five-SMC/stack/visible-scroll and hardware CHR guards.
local C=assert(VEHICLE_AUDIO_CONFIG)
local wall,nmis,windows,stackWrites,minSP,captures=0,0,0,0,255,0
local saved=nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function active()return r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local function storeAt(pc,target)
 return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256
end
local function bankWindow(pc,target,shadow)
 if storeAt(pc,target)then return storeAt(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and storeAt(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and storeAt(pc+2,target)and storeAt(pc-3,shadow)
end
emu.addMemoryCallback(function()
 if not active()then return end
 assert(bank(L.NonMaskableInterrupt)==127,'Bound actual fixed NMI bank')
 local s=emu.getState();local sp=s['cpu.sp']
 saved={a=bank(0xa000),c=bank(0xc000),fields={},sp=sp,cpu_a=s['cpu.a'],sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127}
 local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 saved.aw=saved.a~=saved.sa and bankWindow(pc,0x5115,L.CurrentBank)
 saved.cw=saved.c~=saved.sc and bankWindow(pc,0x5116,L.CurrentBankC)
 for _,at in ipairs(C.smc)do saved.fields[#saved.fields+1]=emu.read(at,emu.memType.nesDebug)end
 nmis=nmis+1;minSP=math.min(minSP,sp)
 assert(sp>=C.stack_floor,'NMI entry retains copied-code stack margin')
end,emu.callbackType.exec,C.nmi)
emu.addMemoryCallback(function()
 if not saved then return end
 assert(bank(0xa000)==(saved.aw and saved.sa or saved.a)and bank(0xc000)==(saved.cw and saved.sc or saved.c),'Audio NMI restores real foreground banks')
 assert((r('CurrentBank')&127)==saved.sa and(r('CurrentBankC')&127)==saved.sc,'Audio NMI restores bank shadows')
 assert(emu.getState()['cpu.a']==saved.cpu_a and emu.getState()['cpu.sp']==saved.sp,'Audio NMI restores A and stack')
 for i,at in ipairs(C.smc)do assert(emu.read(at,emu.memType.nesDebug)==saved.fields[i],'Audio NMI preserves every SMC operand')end
 if saved.aw or saved.cw then windows=windows+1 end
 saved=nil
end,emu.callbackType.exec,C.nmi_return)
local function stackGuard(at,value)
 if not active()then return end
 local sp=emu.getState()['cpu.sp']
 stackWrites=stackWrites+1
 if at==0x100+sp then
  local nextSP=(sp-1)%256
  assert(nextSP>=C.stack_floor,'Actual CPU stack does not cross copied SMC code')
  minSP=math.min(minSP,nextSP)
 end
end
-- Every descending push crosses this first safe byte before reaching copied
-- code. The lower-page guard also catches an invalid direct TXS below it.
-- Avoid callbacks on legitimate high-frequency SMC operand stores themselves.
emu.addMemoryCallback(stackGuard,emu.callbackType.write,0x100+C.stack_floor)
emu.addMemoryCallback(stackGuard,emu.callbackType.write,0x100,0x100+C.stack_start-1)
emu.addMemoryCallback(function(at,value)
 if not active()or r('DisableScreenFlag')~=0 then return end
 local s=emu.getState();local scan=s['ppu.scanline'];local rendering=(r('Mirror_PPUMASK')&24)~=0
 assert(not(rendering and scan>=32 and scan<240),'No music-induced visible world scroll/address write')
end,emu.callbackType.write,0x2005,0x2006)
local chr=dofile(C.chr_observer)({out=OUTPUT,character=19})
emu.addEventCallback(function()
 wall=wall+1
 if C.music==1 and(wall==900 or wall==1800 or wall==5000 or wall==11000)then
  local f=assert(io.open(OUTPUT..'ppu-'..wall..'.png','wb'));f:write(emu.takeScreenshot());f:close();captures=captures+1
 end
end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 if code==0 then
  assert(nmis>100,'Sustained native interrupt/stack-margin coverage')
  chr.finish();assert(not chr.failure(),chr.failure())
  local f=assert(io.open(OUTPUT..'ownership-guards.json','w'))
  f:write(string.format('{"passed":true,"nmis":%d,"mapper_store_windows":%d,"protected_page_write_checks":%d,"minimum_sampled_SP":%d,"SMC_stack_floor":%d,"PPU_screenshots":%d,"five_SMC_operands_preserved":true,"visible_world_PPU_address_writes":0}',nmis,windows,stackWrites,minSP,C.stack_floor,captures));f:close()
 end
 stop(code)
end
