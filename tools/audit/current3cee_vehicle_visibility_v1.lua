-- Added observation layer only: no emulated writes or runtime registrations.
do
local C=assert(VEHICLE_VISIBILITY)
local out=C.output
local bus=assert(io.open(out..'visibility-bus.jsonl','w'))
local snapshots=assert(io.open(out..'visibility-frames.jsonl','w'))
local pubs=assert(io.open(out..'visibility-publications.jsonl','w'))
local ctrl,mask,oamAddress=0,0,0
local drawID,pubID,dmaID,registrations=0,0,0,0
local bodyPending,lastPub,lastDMA,dmaPending,inside=nil,nil,nil,nil,nil
local pages,rows={},0
local function json(v)
 local k=type(v)
 if k=='nil'then return'null'elseif k=='boolean'or k=='number'then return tostring(v)elseif k=='string'then return string.format('%q',v)end
 local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
 for n,x in pairs(v)do a[#a+1]=json(tostring(n))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function stamp()
 local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount'],PC=s['cpu.pc'],SP=s['cpu.sp'],A_bank=bank(0xa000),C_bank=bank(0xc000)}
end
local function wanted()local f=emu.getState()['ppu.frameCount'];return f>=C.first and f<=C.last end
local function live()return r('SelectedCharacter')==C.character and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local function hex(at,n,kind)local a={};for i=0,n-1 do a[#a+1]=string.format('%02x',emu.read(at+i,kind))end;return table.concat(a)end
local function ram()
 local t={};for _,n in ipairs(C.names)do t[n]=r(n)end
 t.arrays={};for n,count in pairs(C.arrays)do t.arrays[n]=hex(C.ram[n],count,emu.memType.nesDebug)end
 return t
end
local function chr()
 local s=emu.getState();local b={}
 for i=0,11 do b[#b+1]=assert(s['mapper.chrBanks'..i])end
 for i=1,8 do local p=b[i];if not pages[p]then
  pages[p]=true;local a={};for j=0,1023 do a[#a+1]=string.char(emu.read(p*1024+j,emu.memType.nesChrRom))end
  local f=assert(io.open(out..'physical-chr-'..p..'.bin','wb'));f:write(table.concat(a));f:close()
 end end
 return b
end
local function row(f,t)t.ppu=t.ppu or stamp();f:write(json(t)..'\n');f:flush()end
local function install(kind,at,fn)registrations=registrations+1;emu.addMemoryCallback(fn,kind,at)end
local function hook(n,fn)local h=assert(C.hooks[n]);install(emu.callbackType.exec,h.address,function()if bank(h.address)==h.bank then fn()end end)end
hook('DrawAllMetasprites',function()
 if not live()then return end
 drawID=drawID+1;bodyPending=nil;inside=nil
end)
hook('DrawMetasprite',function()
 if live()and emu.getState()['cpu.y']==0 then inside=true end
end)
hook('MetaspriteRenderLoop',function()
 if not live()or not inside then return end;inside=nil
 local ptr=r('R0')+256*r('R1');local length=emu.read(ptr,emu.memType.nesDebug)
 assert(length>0 and length<129 and length%4==0,'Actual live body header')
 local start=r('CurrentOAMOffset');local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 local indices={};for i=0,length//4-1 do indices[#indices+1]=((start+rotation+i*4)&255)//4 end
 bodyPending={draw=drawID,entry=stamp(),pointer=ptr,record_bank=bank(ptr),record=hex(ptr,length+1,emu.memType.nesDebug),length=length,logical_start=start,rotation=rotation,indices=indices,header_admitted=start+length<256,x=r('R4')+256*r('R5'),y=r('R6')+256*r('R7'),attr=r('R3'),vflip=r('M1'),ram=ram()}
end)
hook('RosterOamReady',function()
 if not live()then return end
 pubID=pubID+1;local image=hex(C.ram.Sprite_Data,256,emu.memType.nesDebug)
 lastPub={id=pubID,draw=drawID,ppu=stamp(),oam=image,body=bodyPending,ram=ram()}
 if bodyPending then local t={};for _,i in ipairs(bodyPending.indices)do t[#t+1]=image:sub(i*8+1,i*8+8)end;bodyPending.actual_parts=t end
 if wanted()then row(pubs,lastPub)end
end)
install(emu.callbackType.write,0x2000,function(_,v)ctrl=v;if wanted()then row(bus,{kind='PPUCTRL',value=v})end end)
install(emu.callbackType.write,0x2001,function(_,v)mask=v;if wanted()then row(bus,{kind='PPUMASK',value=v})end end)
install(emu.callbackType.write,0x2003,function(_,v)oamAddress=v;if wanted()then row(bus,{kind='OAMADDR',value=v})end end)
install(emu.callbackType.write,0x2004,function(_,v)
 if dmaPending then dmaPending.writes=dmaPending.writes+1;dmaPending.last_write=stamp()
 elseif wanted()then row(bus,{kind='direct-OAMDATA',value=v,address=emu.getState()['ppu.spriteRamAddr']})end
end)
install(emu.callbackType.write,0x4014,function(_,page)
 dmaID=dmaID+1
 lastDMA={id=dmaID,ppu=stamp(),page=page,source=hex(page*256,256,emu.memType.nesDebug),publication=lastPub and lastPub.id,body_draw=lastPub and lastPub.body and lastPub.body.draw,publication_exact=lastPub and hex(page*256,256,emu.memType.nesDebug)==lastPub.oam,mask=mask,ctrl=ctrl,OAMADDR=oamAddress,hardware_OAMADDR=emu.getState()['ppu.spriteRamAddr'],writes=0,ram=ram()};dmaPending=lastDMA
 if wanted()then local t={kind='DMA-start',data=lastDMA};row(bus,t)end
end)
hook('DMA_complete_after_LDX',function()
 if not dmaPending then return end
 local q=dmaPending;dmaPending=nil;q.complete=stamp();q.hardware=hex(0,256,emu.memType.nesSpriteRam);q.hardware_exact_source=q.hardware==q.source
 if wanted()then row(bus,{kind='DMA-complete',id=q.id,publication=q.publication,writes=q.writes,last_write=q.last_write,exact_source=q.hardware_exact_source,source=q.source,hardware=q.hardware,mask=mask,ctrl=ctrl,OAMADDR=emu.getState()['ppu.spriteRamAddr']})end
end)
for _,at in ipairs({0x5120,0x5121,0x5122,0x5123,0x5124,0x5125,0x5126,0x5127,0x5130})do
 install(emu.callbackType.write,at,function(_,v)if wanted()then row(bus,{kind='CHR-register',address=at,value=v})end end)
end
local installed=registrations
local function snapshot(phase)
 if not wanted()then return end
 assert(registrations==installed,'Added observer has no runtime registrations')
 local s=emu.getState();local q=lastDMA
 row(snapshots,{phase=phase,ppu=stamp(),live=live(),ctrl=ctrl,mask=mask,hardware_OAMADDR=s['ppu.spriteRamAddr'],OAMADDR=oamAddress,hardware=hex(0,256,emu.memType.nesSpriteRam),palette=hex(0,32,emu.memType.nesPaletteRam),chr_banks=chr(),DMA=q and q.id,DMA_ppu=q and q.ppu,DMA_writes=q and q.writes,DMA_complete=q and q.complete,DMA_exact=q and q.hardware_exact_source,publication=q and q.publication,body_draw=q and q.body_draw,dma_still_pending=dmaPending~=nil,ram=ram()});rows=rows+1
end
emu.addEventCallback(function()snapshot('startFrame')end,emu.eventType.startFrame)
emu.addEventCallback(function()snapshot('endFrame')end,emu.eventType.endFrame)
local oldStop=emu.stop
emu.stop=function(code)
 bus:close();snapshots:close();pubs:close()
 local f=assert(io.open(out..'added-observer-result.json','w'));f:write(json({rows=rows,static_memory_registrations=installed,final_memory_registrations=registrations,no_added_runtime_registrations=installed==registrations,read_only=true}));f:close()
 oldStop(code)
end
end
