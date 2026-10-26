-- Additive read-only v11 HUD lifecycle/RGB capture. No emulated writes.
local HC=assert(PARODIUS_VISIBILITY)
local HF=assert(io.open(HC.output..'hud-events.jsonl','w'))
local HFR=assert(io.open(HC.output..'hud-frames.jsonl','w'))
local Hserial,Hframes,Hlabels,Hfonts,Hirqs=0,0,0,0,0
local Hstart=nil
local function hr(n)return emu.read(assert(HC.hud_ram[n],n),emu.memType.nesDebug)end
local function hb(a)return emu.convertAddress(a).address//8192 end
local function hs()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount']}end
local function hj(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=hj(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..hj(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hw(f,v)f:write(hj(v)..'\n');f:flush()end
local function hfields()local t={};for n in pairs(HC.hud_ram)do t[n]=hr(n)end;return t end
local function hpacket()local t={};for i=0,83 do t[#t+1]=emu.read(HC.hud_buffer1+i,emu.memType.nesDebug)end;return t end
local function howner()return hr('SelectedCharacter')==18 and hr('VvVariant')==HC.variant and hr('OperMode')==1 and hr('OperMode_Task')==3 and hr('GameEngineSubroutine')==8 end
local function hhook(n,fn)local h=assert(HC.hud_hooks[n]);emu.addMemoryCallback(function()if hb(h.address)~=h.bank then return end;for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Frozen HUD hook '..n)end;fn()end,emu.callbackType.exec,h.address)end
local function hevent(kind,extra)
 local s=emu.getState();local t={kind=kind,ppu=hs(),ram=hfields(),packet=hpacket(),pc=s['cpu.pc'],physical_bank=hb(s['cpu.pc']),SP=s['cpu.sp']};for k,v in pairs(extra or{})do t[k]=v end;hw(HF,t)
end
for _,n in ipairs({'InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty'})do
 emu.addMemoryCallback(function(_,v)if emu.getState()['ppu.frameCount']>=400 then hevent('write-'..n,{previous=hr(n),value=v})end end,emu.callbackType.write,HC.hud_ram[n])
end
for _,n in ipairs({'PnHud','PnHudQueue','PnHudPreUpdateScreen','PnHudCommitAfterVram'})do hhook(n,function()if howner()then Hserial=Hserial+1;hevent('entry-'..n,{id=Hserial})end end)end
hhook('BankSwitchCHR',function()
 if not howner()or HC.variant==0 or hr('InvHudActive')==0 then return end
 assert(hr('InvHudActive')==2*HC.variant+1,'Published HUD exact live variant tag')
 local wanted=assert(HC.hud_labels[tostring(HC.variant)]);for i,v in ipairs(wanted)do assert(emu.read(0x2021+i,emu.memType.nesPpuDebug)==v,'Every published HUD label was actually flushed')end;Hlabels=Hlabels+1
end)
hhook('IrqScrollSplit',function()if howner()and hr('DisableScreenFlag')==0 then assert(emu.getState()['ppu.scanline']==31,'Physical active IRQ split remains line31');Hirqs=Hirqs+1 end end)
emu.addEventCallback(function()
 local s=emu.getState();Hstart={ppu=hs(),ram=hfields(),chr={},labels={},attrs={},palette={}}
 for i=0,11 do Hstart.chr[#Hstart.chr+1]=s['mapper.chrBanks'..i]end
 for i=0,27 do Hstart.labels[#Hstart.labels+1]=emu.read(0x2022+i,emu.memType.nesPpuDebug)end
 for i=0,7 do Hstart.attrs[#Hstart.attrs+1]=emu.read(0x23c0+i,emu.memType.nesPpuDebug)end
 for i=0,31 do Hstart.palette[#Hstart.palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
 if howner()and HC.variant~=0 and hr('InvHudActive')~=0 then
  assert(hr('InvHudActive')==2*HC.variant+1,'Displayed HUD tag matches numeric variant')
  assert(s['mapper.chrBanks8']==395+HC.variant,'Displayed HUD actual font physical page')
  local wanted=HC.hud_labels[tostring(HC.variant)];for i,v in ipairs(wanted)do assert(Hstart.labels[i]==v,'Displayed labels match exact source cells')end;Hfonts=Hfonts+1
 end
end,emu.eventType.startFrame)
emu.addEventCallback(function()
 local stamp=hs();if stamp.frame<HC.hud_capture_start or stamp.frame>HC.hud_capture_end then return end
 local name=string.format('frame-%06d.argb',stamp.frame);local exists=io.open(HC.output..name,'rb')
 if exists then exists:close()else local f=assert(io.open(HC.output..name,'wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end
 Hframes=Hframes+1;hw(HFR,{finished=stamp,start=Hstart,capture=name,mode=hr('CrossoverBehaviorVersion')})
 if stamp.frame==HC.limit then
  assert(Hframes==HC.hud_capture_end-HC.hud_capture_start+1 and Hirqs>=25,'Bounded HUD captures and active physical IRQ evidence')
  if HC.variant~=0 then assert(Hlabels>0 and Hfonts>0,'Actual committed labels and displayed custom font reached')end
  local f=assert(io.open(HC.output..'hud-native-result.json','w'));f:write(hj({passed=true,ROM_sha256=HC.ROM_sha256,mode=hr('CrossoverBehaviorVersion'),variant=hr('VvVariant'),captured_frames=Hframes,label_checks=Hlabels,font_checks=Hfonts,IRQ31_checks=Hirqs,no_emulated_writes=true,limits='Read-only cold control only; no later lifecycle, hardware DMC maximum, starvation or full campaign verdict.'}));f:close();HF:close();HFR:close()
 end
end,emu.eventType.endFrame)
