-- Read-only actual MMC3 cache/bank witness. Controller and source stay untouched.
local C=assert(MMC3_ROUTE_GUARD)
local raw=assert(io.open(C.raw_chr,'rb'));raw=raw:read('*a');assert(#raw==1048576)
local frame,nmis,irqs,uploads,bodyBytes,compositeBytes,dmas=0,0,0,0,0,0,0
local entered=false;local boot=false;local checkedProfile
local ctx,smc;local selector,registers=0,{}
local dirty,verified={},{ }
local first={52,256,276,308,340,380,412,460,460,460,668,708,524,604,304,832,896,960}
local count={116,20,32,32,40,32,48,64,64,64,40,48,80,64,76,64,64,64}
local free={0xc0,0xc2,0xda,0xdc,0xde,0xea,0xf2,0xf6,0xfa,0xfc,0xfe}
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function debug(a)return emu.read(a,emu.memType.nesDebug)end
local function actual(pc)local q=emu.convertAddress(pc);return q and q.address//8192 or -1 end
local function shared()local q={}for a=C.smc_start,C.smc_start+32 do q[#q+1]=debug(a)end;return table.concat(q,',')end
local function live()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('DisableScreenFlag')==0 end
local function hook(h,fn)
 emu.addMemoryCallback(function()
  if actual(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(debug(h.address+i-1)==v,'Exact actual MMC3 immutable hook')end
  fn()
 end,emu.callbackType.exec,h.address)
end
emu.addMemoryCallback(function(_,v)selector=v end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)registers[selector&7]=v end,emu.callbackType.write,0x8001)
emu.addMemoryCallback(function(a,v)error(string.format('MMC3 route wrote MMC5/ExRAM %04x=%02x',a,v))end,emu.callbackType.write,0x5000,0x5fff)
emu.addMemoryCallback(function()
 if actual(0xc000)==228 and r('OperMode')==1 and r('DisableScreenFlag')==0 then
  local s=emu.getState();assert(s['ppu.scanline']>=241 and s['ppu.scanline']<=260,'Native MMC3 cache upload stays in VBlank');uploads=uploads+1
  local bank=registers[2]
  if bank and bank>=132 and bank<168 then dirty[(bank-132)//2]=true end
 end
end,emu.callbackType.write,0x2007)
hook(C.nmi,function()assert(not ctx,'No nested native NMI');ctx=r('CurrentBankC');smc=shared();nmis=nmis+1 end)
hook(C.irq,function()irqs=irqs+1 end)
local function checkComposite(profile)
 local bank=r('M3HardwareSpecial')
 if profile<2 or bank<132 or bank>=168 then return end
 assert(bank%2==0,'Published composite is an aligned pair')
 local slot=(bank-132)//2
 local lo=debug(C.page_lo+slot);local packed=debug(C.page_high+slot//4);local page=lo+256*((packed>>(2*(slot%4)))&3)
 local pairs,bytes={},{}
 for k=0,7 do
  local index=slot*8+k;local v=debug(index<128 and C.masks+index or C.masks_high+index-128);bytes[#bytes+1]=v
  for bit=0,7 do if v&(1<<bit)~=0 then pairs[#pairs+1]=k*8+bit end end
 end
 assert(#pairs<=11,'Actual native composite retains its11-pair admission cap')
 local key=profile..':'..page..':'..table.concat(bytes,',')
 if verified[slot]==key and not dirty[slot]then return end
 local overrides={}
 for index,pair in ipairs(pairs)do
  local destination=1024+(free[index]&0x3e)*16
  for j=0,31 do overrides[destination+j]=assert(raw:byte(page*1024+pair*32+j+1),'Requested source CHR remains inside cartridge art')end
 end
 for i=0,2047 do
  local expected=overrides[i]or raw:byte(2049+i)
  assert(emu.read(bank*1024+i,emu.memType.nesChrRam)==expected,'Displayed native composite matches source art/retained terrain at '..bank..':'..i)
  compositeBytes=compositeBytes+1
 end
 verified[slot]=key;dirty[slot]=false
end
hook(C.nmi_end,function()
 assert(ctx and smc==shared(),'NMI preserves the real foreground farcall SMC')
 assert(actual(0xa000)==r('CurrentBank'),'Native A window restored')
 assert(actual(0xc000)==ctx and r('CurrentBankC')==ctx,'Native C window restored')
 ctx=nil
 if live()and entered then
  assert(selector&128~=0,'Native wide sprite mapping retains MMC3 CHR mode1')
  assert(registers[2]==r('M3HardwareBody')and registers[1]==r('M3HardwareSpecial'),'Actual hardware CHR writes match published body/composite shadows')
  checkComposite(r('M3CacheProfile'))
 end
end)
emu.addMemoryCallback(function()if live()then dmas=dmas+1 end end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 frame=frame+1
 if frame==145 then
  for i=0,262143 do assert(emu.read(i,emu.memType.nesChrRam)==raw:byte(i+1),'Native boot CHR byte '..i)end
  boot=true
 end
 if not live()then return end
 entered=true
 local profile=r('M3CacheProfile');assert(profile>=0 and profile<18,'Native family profile')
 if checkedProfile~=profile then
  for i=0,count[profile+1]*1024-1 do
   assert(emu.read(52*1024+i,emu.memType.nesChrRam)==raw:byte(first[profile+1]*1024+i+1),'Resident native body family matches original raw art')
   bodyBytes=bodyBytes+1
  end
  checkedProfile=profile;verified={};dirty={}
 end
end,emu.eventType.endFrame)
local stop=emu.stop
emu.stop=function(code)
 local f=assert(io.open(ROSTER_CONFIG.out..'mmc3-cache-guard.json','w'))
 f:write(string.format('{"passed":%s,"boot_verified":%s,"entered":%s,"NMI_count":%d,"IRQ_count":%d,"DMA_count":%d,"VBlank_upload_bytes":%d,"resident_body_bytes_verified":%d,"displayed_composite_bytes_verified":%d,"controller_and_game_state_writes":false,"scope":"Native MMC3 full-route bank/SMC, boot, resident-family, displayed composite-source bytes and VBlank cache witness. This is not an independent input replay, exhaustive pose/silhouette/source fidelity or campaign admission."}',tostring(code==0 and boot and entered and nmis>100 and irqs>100 and bodyBytes>0),tostring(boot),tostring(entered),nmis,irqs,dmas,uploads,bodyBytes,compositeBytes));f:close();stop(code)
end
