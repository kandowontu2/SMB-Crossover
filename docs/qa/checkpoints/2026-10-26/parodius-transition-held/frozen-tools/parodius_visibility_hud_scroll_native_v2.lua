-- Exact capture source plus actual displayed scroll and first-prelease RGB.
-- All operations observe emulator state or save evidence; no emulated writes.
local SC=assert(PARODIUS_VISIBILITY)
local SF=assert(io.open(SC.output..'scroll-events.jsonl','w'))
local Sreads,Scaptures,Schecks,Srgb=0,{},0,0
local Sbad,Sstart=nil,nil
local function sr(n)return emu.read(assert(SC.hud_ram[n],n),emu.memType.nesDebug)end
local function sb(a)return emu.convertAddress(a).address//8192 end
local function ss()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount'],t=s['ppu.tmpVideoRamAddr'],v=s['ppu.videoRamAddr'],fineX=s['ppu.xScroll'],w=s['ppu.writeToggle'],background=s['ppu.mask.backgroundEnabled'],sprites=s['ppu.mask.spritesEnabled']}end
local function sj(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=sj(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..sj(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function sw(v)SF:write(sj(v)..'\n');SF:flush()end
local function slive()return sr('SelectedCharacter')==18 and sr('VvVariant')==SC.variant and sr('OperMode')==1 and sr('OperMode_Task')==3 and sr('GameEngineSubroutine')==8 and sr('DisableScreenFlag')==0 end
emu.addMemoryCallback(function()if sb(SC.scroll_capture_entry)==116 then Sreads=0;sw({kind='capture-entry',ppu=ss(),SP=emu.getState()['cpu.sp']})end end,emu.callbackType.exec,SC.scroll_capture_entry)
emu.addMemoryCallback(function()
 local s=emu.getState();local pc=s['cpu.pc'];if sb(pc)==116 and pc>=SC.scroll_capture_entry and pc<SC.scroll_capture_entry+192 then Sreads=Sreads+1 end
end,emu.callbackType.read,0x2007)
emu.addMemoryCallback(function(_,value)
 local s=emu.getState();local pc=s['cpu.pc'];if value~=0 or pc~=SC.scroll_capture_clear_pc or sb(pc)~=116 then return end
 local t=ss();local q={id=#Scaptures+1,kind='capture-clear',ppu=t,reads=Sreads,actual_mode=sr('CrossoverBehaviorVersion'),active=sr('InvHudActive'),mirror_ctrl=sr('Mirror_PPUCTRL'),writer_pc=pc,bank=sb(pc)};Scaptures[#Scaptures+1]=q;sw(q)
 if Sreads~=32 or(t.t&0x73ff)~=0 or t.fineX~=0 or t.w then Sbad={kind='capture scroll restoration',evidence=q}end
end,emu.callbackType.write,SC.hud_ram.PnBombCapturePending)
emu.addEventCallback(function()
 Sstart=nil;if not slive()then return end;local t=ss();Schecks=Schecks+1;Sstart={ppu=t,active=sr('InvHudActive'),font=emu.getState()['mapper.chrBanks8'],labels={}}
 for i=0,27 do Sstart.labels[#Sstart.labels+1]=emu.read(0x2022+i,emu.memType.nesPpuDebug)end
 if t.t~=0 or t.fineX~=0 or t.w then Sbad={kind='actual pre-render HUD scroll',evidence=Sstart}end
 sw({kind='visible-start',state=Sstart})
end,emu.eventType.startFrame)
emu.addEventCallback(function()
 local t=ss();local capture=Scaptures[#Scaptures]
 if capture and capture.ppu.frame==t.frame and Sstart then
  local pixels=emu.getScreenBuffer();local name=string.format('capture-scroll-%06d.argb',t.frame);local f=assert(io.open(SC.output..name,'wb'));for _,v in ipairs(pixels)do f:write(string.pack('<I4',v))end;f:close()
  capture.visible_start=Sstart;capture.finished=t;capture.capture=name
  if Sstart.active==0 then
   assert(Sstart.font==SC.scroll_prelease_blank_source.physical,'Actual prelease native font page')
   for _,v in ipairs(Sstart.labels)do assert(v==SC.scroll_prelease_blank_source.tile,'Actual prelease source blank tile')end
   local backdrop=pixels[8*256+1];local bad=0
   for y=8,15 do for x=16,239 do if pixels[y*256+x+1]~=backdrop then bad=bad+1 end end end
   capture.prelease_RGB={pixels=28*64,bad=bad,observed_backdrop=backdrop,source_tile=36,source_bytes=SC.scroll_prelease_blank_source.bytes};Srgb=Srgb+1;if bad~=0 then Sbad={kind='actual prelease source-blank RGB mask',evidence=capture}end
  end
  sw({kind='capture-visible-frame',capture=capture})
 end
 if Sbad then local f=assert(io.open(SC.output..'first-scroll-failure.json','w'));f:write(sj(Sbad));f:close();assert(false,'Actual capture/prelease scroll or RGB source mismatch; evidence preserved')end
 if t.frame==SC.limit then
  assert(Schecks>=25,'Meaningful actual displayed scroll evidence')
  if SC.variant~=0 then assert(#Scaptures>=1 and Srgb>=1,'Parodius actual capture and first-prelease RGB evidence')end
  local f=assert(io.open(SC.output..'scroll-native-result.json','w'));f:write(sj({passed=true,ROM_sha256=SC.ROM_sha256,actual_mode=sr('CrossoverBehaviorVersion'),actual_variant=sr('VvVariant'),visible_scroll_checks=Schecks,prelease_RGB_checks=Srgb,captures=Scaptures,no_emulated_writes=true,limits='One cold control, register/actual blank-source RGB assertions only; published font/fullscreen visual review and later lifecycle/DMC/overcrowding gates remain.'}));f:close();SF:close()
 end
end,emu.eventType.endFrame)
