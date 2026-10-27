-- Read-only, startup-registration-only observation of exact f1dd body turns.
-- A matched body byte region is distinct from whole-image publication owner.
local C=assert(MM_BODY_OBSERVATION_CONFIG)
local f=assert(io.open(C.output,'w'));f:setvbuf('no')
local rows,bytes,seq,dmas,disabled=0,0,0,0,false
local current,published,dma,bodyPending=nil,nil,nil,false
local ctrl=0
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or -1 end
local function raw(at,count,kind)
 local t={};for i=0,count-1 do t[#t+1]=string.char(emu.read(at+i,kind))end;return table.concat(t)
end
local function hex(v)return(v:gsub('.',function(c)return string.format('%02x',c:byte())end))end
local function region(v,start,count)
 local t={};for i=0,count-1 do t[#t+1]=v:sub((start+i)%256+1,(start+i)%256+1)end;return table.concat(t)
end
local function emit(kind,s,src,hw,whole,bodymatch)
 if disabled then return end
 local q=published or {};local b=q.body or {};local st=emu.getState()
 local v={kind,seq,dmas,st['ppu.frameCount'],st['ppu.scanline'],st['ppu.cycle'],st['cpu.cycleCount'],
  q.seq or 0,q.phase or -1,b.tag or -1,b.logical or -1,b.start or -1,b.count or 0,b.emitted and 1 or 0,
  q.first or -1,q.used or -1,q.rotation or -1,q.current or -1,whole or 0,bodymatch or 0,
  q.x or -1,q.y or -1,q.camera or -1,q.types or '',q.ages or '',ctrl,hex(src or ''),hex(hw or '')}
 local line=table.concat(v,',')..'\n'
 if rows>=C.maximum_rows or bytes+#line>C.maximum_bytes then
  f:write('CAP,',tostring(rows),',',tostring(bytes),'\n');f:close();disabled=true;return
 end
 f:write(line);rows=rows+1;bytes=bytes+#line
end
f:write('kind,construction,dma,ppu_frame,line,dot,cpu_cycle,published_construction,source_phase,tag,body_logical,body_physical,body_bytes,emitted,first,used,rotation,current,full_source_owner,body_region_same,player_x,player_y,camera,shot_types,shot_ages,actual_ctrl,source_body_hex,physical_body_hex\n')
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function(pc)
  if disabled or bank(pc)~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Body observation hook bytes '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
hook('draw',function()
 seq=seq+1;bodyPending=false;current=nil
 if r('SelectedCharacter')==1 then current={seq=seq,phase=r('SpriteShuffleOffset')&1}end
end)
hook('body_entry',function(s)
 if current and s['cpu.y']==0 then bodyPending=true end
end)
hook('header',function(s)
 if not bodyPending or not current then return end
 local logical=r('CurrentOAMOffset');local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 current.body={logical=logical,start=(logical+rotation)%256,count=s['cpu.y'],tag=r('GuestOamRotationActive'),emitted=false}
end)
hook('loop_end',function(s)
 if not bodyPending or not current or not current.body then return end
 local b=current.body;b.emitted=((s['cpu.x']-b.start)%256==b.count)
 bodyPending=false
end)
hook('publish',function()
 if not current then return end
 local q=current
 q.image=raw(0x200,256,emu.memType.nesDebug)
 q.first=r('RgOamFirst');q.used=r('RgOamUsed');q.rotation=r('RgOamRotation');q.current=r('CurrentOAMOffset')
 q.x=r('Player_X_Position')+256*r('Player_PageLoc');q.y=r('Player_Y_Position')
 q.camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 q.types=hex(raw(C.ram.MmBulletType,4,emu.memType.nesDebug));q.ages=hex(raw(C.ram.MmBulletAge,4,emu.memType.nesDebug))
 published=q;current=nil;bodyPending=false
 local b=q.body or {start=0,count=0}
 emit('P',nil,region(q.image,b.start,b.count),'',1,1)
end)
-- Every callback is registered once, before emulator execution. No runtime
-- add/remove callback is performed by a body/return callback.
emu.addMemoryCallback(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(_,page)
 dma={source=raw(page*256,256,emu.memType.nesDebug),page=page}
end,emu.callbackType.write,0x4014)
hook('dma_complete',function()
 if not dma then return end
 dmas=dmas+1;local q=published;local b=q and q.body or {start=0,count=0}
 local src=region(dma.source,b.start,b.count)
 local hw=region(raw(0,256,emu.memType.nesSpriteRam),b.start,b.count)
 local whole=q and dma.source==q.image and 1 or 0
 local same=q and src==region(q.image,b.start,b.count)and 1 or 0
 -- Source and physical bytes are deliberately unmasked. The existing route
 -- guard separately owns E3 hardware-attribute interpretation/full256 proof.
 emit('D',nil,src,hw,whole,same);dma=nil
end)
