-- Additive read-only all-identity timing evidence. Original six guards stay intact.
do
local C=assert(PARODIUS_VISIBILITY)
local T=assert(C.early_timing)
local file=assert(io.open(C.output..'menu-early-timing.jsonl','w'))
local mask,pending,lastNMI,lastParser=0,nil,nil,nil
local dmas,completed,enables,late,hardwareBad,menuFrames=0,0,0,0,0,0
local function json(v)
 if type(v)=='table'then local out={};if#v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end;for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function stamp()
 local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],cpu=s['cpu.cycleCount'],PC=s['cpu.pc'],SP=s['cpu.sp']}
end
local function row(q)file:write(json(q)..'\n');file:flush()end
local function r(n)return emu.read(assert(T.ram[n],n),emu.memType.nesDebug)end
local function bytes(at,n,kind)local q={};for i=0,n-1 do q[#q+1]=emu.read(at+i,kind or emu.memType.nesDebug)end;return q end
local function equal(a,b)if#a~=#b then return false end;for i,v in ipairs(a)do if b[i]~=v then return false end end;return true end
local function scope()
 if r('DisableScreenFlag')~=0 then return false end
 return r('CrossoverMenuState')==2 and r('OperMode')==0 or r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
-- Exact predicate from ROOT presentation_timing_preflight_v1.lua.
local function safe(line,dot)return line>=241 and line<=260 or line==-1 and dot<=274 end
local function hook(n,fn)
 local h=assert(T.hooks[n],n)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.pc);if not p or p.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Early actual hook '..n)end
  fn()
 end,emu.callbackType.exec,h.pc)
end
hook('NmiEntry',function()lastNMI=stamp();row({kind='early-NMI-entry',ppu=lastNMI,scope=scope()})end)
hook('UpdateScreen',function()
 local ptr=r('NmiR0')+256*r('NmiR1')
 lastParser={ppu=stamp(),pointer=ptr,packet=bytes(ptr,128),scope=scope()}
 row({kind='early-VRAM-parser',parser=lastParser})
end)
emu.addMemoryCallback(function(_,v)
 local old=mask;mask=v;local p=stamp()
 if old&24==0 and v&24~=0 then
  local scoped=scope();local ok=safe(p.scanline,p.dot)
  if scoped then enables=enables+1;if not ok then late=late+1 end end
  row({kind='early-render-enable',ppu=p,mask=v,scope=scoped,safe=ok,last_NMI=lastNMI,last_parser=lastParser,menu=r('CrossoverMenuState'),oper=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine')})
  assert(not scoped or ok,'Scoped render enable before pre-render vertical reload (274 margin)')
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 assert(not pending,'Early no pending actual DMA')
 local s=emu.getState();local h=T.hooks.DmaBefore
 assert(s['cpu.pc']==h.pc and v==2,'Early real page2 DMA instruction')
 local physical=emu.convertAddress(s['cpu.pc']);assert(physical and physical.address//8192==h.bank,'Early real DMA physical bank')
 for i,x in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==x,'Early actual post-DMA sequence')end
 assert(mask&24==0,'Early rendering disabled before every DMA')
 dmas=dmas+1;pending={id=dmas,start=stamp(),source=bytes(v*256,256),writes=0,start_mask=mask,scope=scope(),last_NMI=lastNMI,last_parser=lastParser}
 row({kind='early-DMA-start',DMA=pending})
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 assert(pending,'Early every OAM write belongs to observed actual DMA')
 pending.writes=pending.writes+1;if pending.writes==1 then pending.first=stamp()end;pending.last=stamp()
 assert(mask&24==0,'Early disabled rendering at every actual DMA data write')
end,emu.callbackType.write,0x2004)
hook('DmaComplete',function()
 if not pending then return end
 local q=pending;pending=nil;q.complete=stamp();q.hardware=bytes(0,256,emu.memType.nesSpriteRam);q.end_mask=mask;q.exact_source=equal(q.source,q.hardware)
 completed=completed+1;if not q.exact_source then hardwareBad=hardwareBad+1 end
 row({kind='early-DMA-complete',DMA=q})
 assert(q.writes==256 and mask&24==0,'Early actual 256 writes completed before enable')
 assert(q.exact_source,'Early complete physical256 exact immutable source')
end)
-- Full source/physical ownership is recorded for a separate post-run background
-- oracle; recording it is not itself a whole-background pixel verdict.
emu.addEventCallback(function()
 local s=emu.getState()
 if r('OperMode')~=0 or r('CrossoverMenuState')~=2 or r('DisableScreenFlag')~=0 or not s['ppu.mask.backgroundEnabled']then return end
 local chr={};for i=0,11 do chr[#chr+1]=s['mapper.chrBanks'..i]end
 row({kind='early-menu-start-owner',ppu=stamp(),t=s['ppu.tmpVideoRamAddr'],v=s['ppu.videoRamAddr'],fineX=s['ppu.xScroll'],w=s['ppu.writeToggle'],
      mask=mask,actual_chr=chr,palette=bytes(0x3f00,32,emu.memType.nesPpuDebug),nametables=bytes(0x2000,4096,emu.memType.nesPpuDebug),
      hardware_OAM=bytes(0,256,emu.memType.nesSpriteRam),selected=emu.read(C.ram.SelectedCharacter,emu.memType.nesDebug),variant=emu.read(C.ram.VvVariant,emu.memType.nesDebug)})
 menuFrames=menuFrames+1
end,emu.eventType.startFrame)
-- Registered before all original endFrame finalizers/stop; no runtime callback API.
emu.addEventCallback(function()
 local p=stamp();if p.frame~=C.limit then return end
 assert(not pending,'Early terminal no pending DMA')
 assert(completed==dmas and completed>500 and enables>100 and menuFrames>100 and late==0 and hardwareBad==0,'Meaningful all-identity early timing scope')
 local f=assert(io.open(C.output..'menu-timing-native-result.json','w'))
 f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,all_identity_completed_DMAs=completed,scoped_render_enables=enables,menu_start_owner_frames=menuFrames,late_enables=late,hardware_mismatches=hardwareBad,no_emulated_writes=true,limits='Actual ungated DMA256/E008/PPUMASK observations in this menu1800 only. Scoped enable before pre-render274; original six semantic guard layers independent. Full menu NT/CHR/palette/OAM snapshots are inputs to separate post-run pixel review, not a wholeBG verdict. No global worst-DMC/campaign/flicker claim.'}));f:close();file:close()
end,emu.eventType.endFrame)
end
