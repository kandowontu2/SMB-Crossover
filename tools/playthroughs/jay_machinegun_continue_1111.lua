local gun=coroutine.create(function()
 assert(flagReached and castleReached,'Native 1-1 flag and castle')
 wait(function()
  return active() and read(0x761)==1 and read(0x753)==2 and
   ram(2,0xc9)==1 and read(0xbd)==176 and ram(2,donorFlags-0xc000)&4==0
 end)
 assert(ram(2,0xcb)==1 and ram(2,0xbf)==3,'Machine gun earned in underground 1-2')
 assert(ram(2,0xbe)==63 and ram(2,0x20)==0,'Underground starts on stock with 63 ammo')
 press(16)
 assert(read(0x777)&1~=0,'Native underground pause')
 press(32)
 assert(ram(2,0x20)==1,'Select earned machine gun')
 wait(function()return read(0x777)&0x80==0 end)
 press(16)
 assert(read(0x777)&1==0,'Native underground resume')
 bits=64
 wait(function()return #gunBirths>=5 end)
 bits=0
 for i=0x60,0xa0,0x10 do assert(ram(2,i+9)~=0,'Five live machine gun slots')end
 for _=1,8 do coroutine.yield()end
 assert(#gunBirths==5 and ram(2,0xbe)==58 and ram(2,0x20)==1,'Five held-B shots cost five ammo')
 assert(gunDma>0 and gunExtendedDma>0,'Native DMA for the two added projectile slots')
 assert(read(0x75f)==2,'Two lives through 1-2 machine gun test')
 finish(true,'Jay cleared 1-1, selected the earned machine gun, and fired five held-B shots in 1-2')
end)
emu.addMemoryCallback(guard('Machine gun birth',function()
 local pc=0xa7da
 if phase~='machinegun' or not mapped(pc,pc-0xa000)then return end
 assert(header(2)==cookie and header(3)==cookie,'Machine gun cache headers')
 local x=emu.getState()['cpu.x']
 local slot=x-0x50
 local clock=read(0x0e)
 assert(x==0xf0-16*#gunBirths and read(0xdc)&64~=0,'Original machine gun slot order and held B')
 assert(ram(2,0xbe)==62-#gunBirths and ram(2,0x1c)==4,'Original ammo spend and cooldown')
 assert(ram(2,slot+4)==0x50 and ram(2,slot+5)==0 and ram(2,slot+8)==0 and ram(2,slot+15)==1,
  'Original machine gun projectile record')
 if gunLastClock then assert((clock-gunLastClock)&255==5,'Five native updates between held-B shots')end
 gunLastClock=clock
 gunBirths[#gunBirths+1]=string.format('[%d,%d,%d]',clock,x,ram(2,0xbe))
end),emu.callbackType.exec,0xa7da)
