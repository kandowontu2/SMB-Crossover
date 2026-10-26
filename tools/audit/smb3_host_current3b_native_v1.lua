-- Additive read-only source/music observation. Every host callback is installed
-- before execution; dynamic returns are Lua-only slots in one startup dispatcher.
local C=assert(SMB3_MUSIC_NATIVE_CONFIG)
local out=assert(ROSTER_CONFIG.out)
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function physical(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function stamp()
 local s=emu.getState();return{cpu=s['cpu.cycleCount'],frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],pc=s['cpu.pc'],bank=physical(s['cpu.pc']),sp=s['cpu.sp']}
end
local function json(v)
 if type(v)=='table'then
  local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',k)..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local file=assert(io.open(out..'smb3-music-native.jsonl','w'))
local function row(v)file:write(json(v)..'\n');file:flush()end
local function regs(s)return{s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p'],s['cpu.sp']}end
local function state()
 local q={};for _,a in ipairs(C.source_state_addresses)do q[#q+1]=emu.read(a,emu.memType.nesDebug)end;return q
end
local function eq(a,b)if #a~=#b then return false end;for i,x in ipairs(a)do if x~=b[i]then return false end end;return true end
local function hook(n,fn)
 local h=assert(C.hooks[n]);emu.addMemoryCallback(function()
  local b=physical(h.pc);local allowed=false;for _,v in ipairs(h.banks)do if b==v then allowed=true end end
  if not allowed then assert(not h.resident,'Unexpected resident physical owner '..n..':'..b);return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Real music hook bytes '..n)end
  fn(emu.getState(),b)
 end,emu.callbackType.exec,h.pc)
end
local pending,returns={},{}
local function onReturn(n,fn)
 local s=emu.getState();local sp=s['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local start=physical(ret);local signature={};for i=0,7 do signature[#signature+1]=emu.read(ret+i,emu.memType.nesDebug)end
 assert(not pending[n],'No overlapping music return '..n)
 pending[n]={pc=ret,sp=(sp+2)%256,bank=start,fn=fn,signature=signature}
 returns[ret]=true
end
local function alias(a,b,old)
 if b==old then return true end
 if a<0xe000 then return false end
 local found,previous=false,false;for _,v in ipairs(C.resident_aliases)do if b==v then found=true end;if old==v then previous=true end end
 return found and previous
end
local source=nil
local calls,plays,inits,audioCalls,sourceImageWrites,starts,fetches,completions=0,0,0,0,0,0,0,0
local activeAliases={};local lastAPU={};local liveDmc=nil;local lastEnable=0
local sourceWriteKeys={};for _,a in ipairs(C.source_state_addresses)do sourceWriteKeys[a]=true end
local function sourceEntry(kind,s,b)
 assert(not source,'No recursive source driver call');calls=calls+1
 if kind=='init'then inits=inits+1 else plays=plays+1 end
 source={serial=calls,kind=kind,entry=stamp(),registers=regs(s),logical={},RAM={},maps={},start_state=state()}
 onReturn('source',function(st,retBank)
  local q=source;assert(q,'Source return owner');source=nil
  q.complete=stamp();q.return_bank=retBank;q.return_registers=regs(st);q.finish_state=state()
  row({kind='original-source-call',call=q})
 end)
end
hook('SourceInit',function(s,b)sourceEntry('init',s,b)end)
hook('SourcePlay',function(s,b)sourceEntry('play',s,b)end)
hook('AudioUpdate',function(s,b)
 audioCalls=audioCalls+1;local begun=stamp();local oldA=r('CurrentBank');local oldC=r('CurrentBankC');local saved={};for i=0,5 do saved[#saved+1]=emu.read(C.zp+i,emu.memType.nesDebug)end
 activeAliases[tostring(b)]=(activeAliases[tostring(b)]or 0)+1
 onReturn('audio',function(st,retBank)
  assert(r('CurrentBank')==oldA and r('CurrentBankC')==oldC,'Actual wholeAudio foreground bank shadows restored')
  local after={};for i=0,5 do after[#after+1]=emu.read(C.zp+i,emu.memType.nesDebug)end;assert(eq(saved,after),'Actual live foreground decoder ZP restored')
  row({kind='whole-audio-return',entry=begun,complete=stamp(),return_bank=retBank,cycles=st['cpu.cycleCount']-begun.cpu,owner=r('BassDmcActive'),priority=r('Cv3DmcPriority'),E=physical(0xe000),worldQueues={r('GuestWorldQueues'),r('GuestWorldQueues',1),r('GuestWorldQueues',2)},worldMask=r('GuestMixMask'),nativeMask=r('GuestNativeEnable')})
 end)
end)
emu.addMemoryCallback(function(a,v)
 if source then source.logical[#source.logical+1]={0x4000+a-C.ram.GuestNativeApu,v};sourceImageWrites=sourceImageWrites+1 end
end,emu.callbackType.write,C.ram.GuestNativeApu,C.ram.GuestNativeApu+15)
for _,n in ipairs({'B3Source4012','B3Source4015'})do
 local register=n=='B3Source4012'and 0x4012 or 0x4015
 emu.addMemoryCallback(function(_,v)if source then source.logical[#source.logical+1]={register,v}end end,emu.callbackType.write,C.ram[n])
end
for _,a in ipairs(C.source_state_addresses)do
 emu.addMemoryCallback(function(_,v)if source then source.RAM[#source.RAM+1]={a,v}end end,emu.callbackType.write,a)
end
emu.addMemoryCallback(function(a,v)if source then source.maps[#source.maps+1]={0x5ff8+a-C.ram.B3VirtualMaps,v}end end,emu.callbackType.write,C.ram.B3VirtualMaps,C.ram.B3VirtualMaps+7)
local function dmcState()
 local q={};for k,v in pairs(emu.getState())do if tostring(k):lower():find('dmc')then q[k]=v end end;return q
end
emu.addMemoryCallback(function(a,v)
 lastAPU[a]=v
 if source and a>=0x4010 and a~=0x4012 and a~=0x4015 then source.logical[#source.logical+1]={a,v}end
 row({kind='physical-APU',stamp=stamp(),register=a,value=v,source_serial=source and source.serial,owner=r('BassDmcActive'),E=physical(0xe000)})
 if a~=0x4015 then return end
 if v&16==0 and liveDmc then liveDmc.stopped=true end
 if v&16~=0 and lastEnable==0 and r('BassDmcActive')==4 then
  local e=physical(0xe000);assert(e==70 or e==97,'SMB3 DMC owns actual regenerated E70/97')
  local start=0xc000+64*assert(lastAPU[0x4012]);local len=16*assert(lastAPU[0x4013])+1;local logical=0xc000+64*r('B3Source4012');local payload={}
  assert(start>=0xf140 and start+len<=0xfd42,'Declared actual SMB3 DMC span')
  for i=0,len-1 do
   local at=(logical+i)%65536;local page=r('B3VirtualMaps',(at-0x8000)//4096);local physicalROM=assert(C.payload_banks[page+1],'Original source virtual page')*8192+4096+at%4096
   local expected=emu.read(physicalROM,emu.memType.nesPrgRom);assert(emu.read(start+i,emu.memType.nesDebug)==expected,'Actual cloned-E sample binding equals retained original payload')
   payload[#payload+1]=expected
  end
  starts=starts+1;liveDmc={serial=starts,start=start,payload=payload,reads=0,bank=e,stopped=false,request=stamp(),sourceLogical=logical,initial=dmcState()}
  row({kind='DMC-start',request=liveDmc})
 end
 lastEnable=v&16
end,emu.callbackType.write,0x4000,0x4017)
emu.addMemoryCallback(function(a,v)
 if not liveDmc or liveDmc.stopped or liveDmc.reads>=#liveDmc.payload then return end
 if a<liveDmc.start or a>=liveDmc.start+#liveDmc.payload then return end
 assert(physical(a)==liveDmc.bank,'Actual DMC fetch physical clone')
 assert(a==liveDmc.start+liveDmc.reads and v==liveDmc.payload[liveDmc.reads+1],'Actual sequential DMC fetch/value')
 liveDmc.reads=liveDmc.reads+1;fetches=fetches+1
 row({kind='DMC-fetch',serial=liveDmc.serial,address=a,value=v,stamp=stamp()})
 if liveDmc.reads==#liveDmc.payload then completions=completions+1;row({kind='DMC-fetch-complete',serial=liveDmc.serial,stamp=stamp(),actual_state=dmcState()})end
end,emu.callbackType.read,0xf140,0xfd41)
emu.addMemoryCallback(function(_,v)
 row({kind='real-E-publication',value=v,stamp=stamp(),owner=r('BassDmcActive'),source_serial=source and source.serial})
end,emu.callbackType.write,0x5117)
local frames,active=0,0
emu.addEventCallback(function()
 frames=frames+1
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  active=active+1;assert(r('SelectedCharacter')==17 and r('M3Variant')==0 and r('CrossoverBehaviorVersion')==0,'Actual cold SMB3 Mario Easy identity')
 end
end,emu.eventType.endFrame)
SMB3_MUSIC_INSTALL_RETURN_DISPATCHER=function()
 emu.addMemoryCallback(function(pc)
  if not returns[pc]then return end
  local st=emu.getState();local b=physical(pc)
  for name,q in pairs(pending)do
   if q.pc==pc and st['cpu.sp']==q.sp and alias(pc,b,q.bank)then
    for i,v in ipairs(q.signature)do assert(emu.read(pc+i-1,emu.memType.nesDebug)==v,'Genuine music return bytes across E aliases')end
    pending[name]=nil;q.fn(st,b)
   end
  end
 end,emu.callbackType.exec,0,65535)
end
local stop=emu.stop
emu.stop=function(code)
 local p={passed=code==0 and active>300 and inits>0 and plays>300 and sourceImageWrites>0,frames=frames,active_frames=active,source_calls=calls,source_init=inits,source_play=plays,audio_calls=audioCalls,source_image_writes=sourceImageWrites,DMC_starts=starts,DMC_fetches=fetches,DMC_complete_fetches=completions,audio_entry_physical_aliases=activeAliases,source_call_pending=source~=nil,actual_mode=r('CrossoverBehaviorVersion'),actual_character=r('SelectedCharacter'),actual_variant=r('M3Variant'),ROM_sha256=C.ROM_sha256,no_fixture_state_writes=true,native_waveform_qualification=false,matching_parent_cadence_control_available=false}
 row({kind='native-summary',summary=p});file:close();local f=assert(io.open(out..'smb3-music-native-result.json','w'));f:write(json(p)..'\n');f:close();stop(code)
end
