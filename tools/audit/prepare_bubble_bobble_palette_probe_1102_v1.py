"""Passive cold palette/queue first-write trace; no candidate changes or emulator."""
import json
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
from prepare_bub_menu_qualification_1102_v2 import lua
from prepare_selected_native_packet_v1 import prepare
P=Q.P;N=Q.N;R=Q.R;O=Q.O;address=Q.address
ROM=R/'build/bub-menu-candidate-1102-v2/combined2.nes';PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'


def main():
 assert P.sha(ROM.read_bytes())==PIN
 parent=R/'build/bub-menu-candidate-1102-v2/native-combined2-bub-cold'
 assert json.loads((parent/'capture/result.json').read_text())['passed']
 b=P.scoped_load(P.ROM);q=json.loads((O/'native-proxy-layout.json').read_text());hooks={}
 for name in['GetBackgroundColor','GetPlayerColors','HuNativeWorldPalette','X5QueueAreaBackdrop','GetAreaPalette']:
  if name not in b['syms']:continue
  pc=address(b,name);at=Q.Q.Q.location(b,name);hooks[name]=dict(name=name,pc=pc,memory='nesPrgRom',physical=at-16,bytes=list(ROM.read_bytes()[at:at+3]))
 pc=q['labels']['BbHelperColors'];art=(O/'native-proxy-helper.chr').read_bytes();hooks['BbHelperColors']=dict(name='BbHelperColors',pc=pc,memory='nesWorkRam',physical=2*8192+(pc&8191),bytes=list(art[pc-0xd000:pc-0xd000+3]))
 names=['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','AreaType','BackgroundColorCtrl','VRAM_Buffer1','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl','SmFreezePaletteControl','CurrentBank','CurrentBankC','ScreenRoutineTask','NmiDisable','CurrentCHRBank','X5ChrMode','X5WideChrActive','Mirror_PPUCTRL','Mirror_PPUMASK']
 cfg=dict(ROM_sha256=PIN,ram={n:address(b,n)for n in names},hooks=hooks)
 observer=r'''
local C=BUB_PALETTE_PROBE
local count,frame,control,latch,address=0,0,0,0,0
local records,snapshots,calls,returnHooks={},{},{},{}
local firstActive,colorPending=false,nil
local upper,chr=0,{}
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return read(C.ram[n])end
local function rgb()local a={};for i=0,31 do a[#a+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end;return a end
local function queue()local a={};for i=0,math.min(83,r('VRAM_Buffer1_Offset')+1)do a[#a+1]=read(C.ram.VRAM_Buffer1+i)end;return a end
local function snapshot(tag)
 if #snapshots>=24 then return end
 snapshots[#snapshots+1]={tag=tag,frame=frame,cycle=emu.getState()['cpu.cycleCount'],mode=r('OperMode'),task=r('OperMode_Task'),game=r('GameEngineSubroutine'),screen_task=r('ScreenRoutineTask'),raw=r('SelectedCharacter'),area=r('AreaType'),background_ctrl=r('BackgroundColorCtrl'),VRAM_ctrl=r('VRAM_Buffer_AddrCtrl'),freeze_ctrl=r('SmFreezePaletteControl'),buffer=queue()}
end
local function valid(h)
 local a=emu.convertAddress(h.pc)
 if not a or a.memType~=emu.memType[h.memory]or a.address~=h.physical then return false end
 for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Pinned passive palette hook '..h.name)end
 return true
end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end;for k,x in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return 'null'else return tostring(v)end
end
for name,h in pairs(C.hooks)do
 emu.addMemoryCallback(function()
  if r('SelectedCharacter')~=39 or not valid(h)then return end
  calls[name]=(calls[name]or 0)+1;snapshot('enter-'..name)
  if name=='BbHelperColors'then
   local s=emu.getState();local sp=s['cpu.sp'];local ret=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
   colorPending={ret=ret,sp=(sp+2)&255}
   if not returnHooks[ret]then returnHooks[ret]=true;emu.addMemoryCallback(function()if colorPending and colorPending.ret==ret and colorPending.sp==emu.getState()['cpu.sp']then colorPending=nil;snapshot('returned-BbHelperColors')end end,emu.callbackType.exec,ret)end
  end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function(_,v)control=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function()latch=0 end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function()latch=1-latch end,emu.callbackType.write,0x2005)
emu.addMemoryCallback(function(_,v)if latch==0 then address=((v&63)<<8)|(address&255)else address=(address&0x3f00)|v end;latch=1-latch end,emu.callbackType.write,0x2006)
emu.addMemoryCallback(function()address=(address+((control&4~=0)and 32 or 1))&16383 end,emu.callbackType.read,0x2007)
emu.addMemoryCallback(function(_,v)
 if address>=0x3f00 and address<0x4000 and(r('SelectedCharacter')==39 or r('OperMode')==1)then
  count=count+1
  if #records<200 then
   local s=emu.getState();local index=address&31;if index>=16 and index%4==0 then index=index-16 end
   records[#records+1]={n=count,frame=frame,cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],raw_A=r('CurrentBank'),raw_C=r('CurrentBankC'),PPU_address=address,normalized_index=index,value=v,raw=r('SelectedCharacter'),mode=r('OperMode'),game=r('GameEngineSubroutine'),VRAM_ctrl=r('VRAM_Buffer_AddrCtrl')}
  end
 end
 address=(address+((control&4~=0)and 32 or 1))&16383
end,emu.callbackType.write,0x2007)
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)chr[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
local function bubPaletteFinish()
 snapshot('final')
 local s=emu.getState();local actual,software,modes,nt,attr={},{},{},{},{}
 for i=0,11 do actual[#actual+1]=s['mapper.chrBanks'..i]or -1;software[#software+1]=read(C.ram.CurrentCHRBank+i);modes[#modes+1]=read(C.ram.X5ChrMode+i)end
 for i=0,63 do nt[#nt+1]=emu.read(0x2040+i,emu.memType.nesPpuDebug)end
 for i=0,7 do attr[#attr+1]=emu.read(0x23c0+i,emu.memType.nesPpuDebug)end
 local final={palette=rgb(),hardware_CHR=actual,last_5120_512B_writes=chr,upper_5130=upper,software_CHR=software,software_CHR_modes=modes,wide_active=r('X5WideChrActive'),PPUCTRL=r('Mirror_PPUCTRL'),PPUMASK=r('Mirror_PPUMASK'),HUD_NT_2040_207F=nt,HUD_attributes_23C0_23C7=attr}
 local f=assert(io.open(OUTPUT..'bub-palette-probe.json','w'));f:write(json({ROM_sha256=C.ROM_sha256,passive=true,script_RAM_writes=false,frame=frame,total_palette_writes=count,records_truncated=count>#records,calls=calls,records=records,snapshots=snapshots,final=final}));f:close()
end
emu.addEventCallback(function()
 frame=frame+1
 if not firstActive and r('SelectedCharacter')==39 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then firstActive=true;snapshot('first-native-active8')end
end,emu.eventType.endFrame)
'''
 controller=(parent/'controller.lua').read_text();assert controller.count('local function finish()')==1
 controller=controller.replace('local function finish()','local function finish()\n bubPaletteFinish()',1)
 text='local BUB_PALETTE_PROBE='+lua(cfg)+'\n'+observer+'\n'+controller
 output=O/'native-palette-probe-1102-v1'
 prepare(output,ROM,text,[Path(__file__),parent/'controller.lua',parent/'capture/result.json',O/'native-proxy-qualified-1102-v5.json',R/'docs/qa/allocations/bubble-shared-native-1102-v5.json'],expected=PIN,timeout=120,allow_interactive=True,scope='Exact passed cold Bub controller plus passive first200PPUpalettewrites/24sourcequeueevents andonefinal32palette+BGCHR+HUDNT/attribute snapshot inoneJSON. OriginalonePNG unchanged; no input/state/candidate changes or speculative repair.')
 # Compare the actual safe helper packet with the genuine native world leaf.
 cb,layout,route=Q.bundle();m=Q.fresh(cb,route);N.put(m,VRAM_Buffer1_Offset=0)
 N.invoke(m,'GetPlayerColors',x=0,y=0);helper=list(m[address(cb,'VRAM_Buffer1'):address(cb,'VRAM_Buffer1')+N.get(m,'VRAM_Buffer1_Offset')+1])
 N.put(m,VRAM_Buffer1_Offset=0);N.invoke(m,'HuNativeWorldPalette',x=0,y=0);world=dict(Buffer1=list(m[address(cb,'VRAM_Buffer1'):address(cb,'VRAM_Buffer1')+N.get(m,'VRAM_Buffer1_Offset')+1]),VRAM_ctrl=N.get(m,'VRAM_Buffer_AddrCtrl'),freeze_ctrl=N.get(m,'SmFreezePaletteControl'))
 receipt=dict(prepared=True,native=False,ROM_sha256=PIN,helper_actual_native_GetPlayerColors_queue=helper,genuine_HuNativeWorldPalette_queue=world,interpretation='Nativearea GroundPaletteData starts0F29/1A BG0. HelperopaqueRGB doesnotperform nativeworld/backdrop/HUD packet. Actualfirst-write nativeprobe remainsrequired; norepairyet.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),output/'controller.lua',output/'ready.json']})
 (O/'palette-probe-prepared-1102-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(prepared=True,output=output.relative_to(R).as_posix(),helper_packet=helper,native_world_packet=world,native=False)))


if __name__=='__main__':main()
