-- Borrowed native block-update arena, restored at the actual caller return.
-- Numeric queue state and replacement flags are authored; this is not a route.
local C=assert(HUD_CONSUMER_CONFIG)
dofile(C.bootstrap)
local frame,index,active=0,1,nil
local registered={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function physical(pc)local q=emu.convertAddress(pc);return q and q.memType==emu.memType.nesPrgRom and q.address//8192 or-1 end
local function bind(h,fn)
 emu.addMemoryCallback(function()
  if physical(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual native consumer bytes')end
  fn()
 end,emu.callbackType.exec,h.address)
end
bind(C.write,function()
 if not active then return end
 active.writes=active.writes+1
 assert(active.pending==0,'Pending numeric HUD work must prevent native terrain replacement, case '..index)
end)
bind(C.entry,function()
 if active or frame<550 or r('GameEngineSubroutine')~=8 then return end
 assert(r('SelectedCharacter')==7,'Actual Rygar menu selection')
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local pending=index<=126 and (index-1)%63+1 or 0
 local header=index<=63 and 0 or index<=126 and 0x20 or 0
 local ram={};for i=0,2047 do ram[i]=emu.read(i,emu.memType.nesDebug)end
 local previous=emu.read(C.pending,emu.memType.nesDebug)
 active={ram=ram,previous=previous,pending=pending,header=header,writes=0,pc=pc,bank=physical(pc),sp=(sp+2)%256}
 for i=0,83 do w('VRAM_Buffer1',0,i)end
 w('VRAM_Buffer1_Offset',0);w('VRAM_Buffer1',header)
 emu.write(C.pending,pending,emu.memType.nesDebug)
 for i=0,1 do
  w('Block_RepFlag',1,i);w('Block_Metatile',0x52,i)
  w('Block_BBuf_Low',(L.Block_Buffer_1+i)%256,i)
  w('Block_Orig_YPos',128,i);w('Block_X_Position',32+i*16,i);w('Block_PageLoc',0,i)
 end
 if registered[pc]then return end
 registered[pc]=true
 emu.addMemoryCallback(function()
  if not active or active.pc~=pc or physical(pc)~=active.bank or emu.getState()['cpu.sp']~=active.sp then return end
  if active.pending>0 then
   assert(active.writes==0 and r('Block_RepFlag',0)==1 and r('Block_RepFlag',1)==1,'Both slots remain deferred while pending')
  else
   assert(active.writes==1 and r('Block_RepFlag',0)==1 and r('Block_RepFlag',1)==0,'No pending work preserves native one-packet admission: slot1 fills queue and slot0 waits')
  end
  for i=0,2047 do emu.write(i,active.ram[i],emu.memType.nesDebug)end
  emu.write(C.pending,active.previous,emu.memType.nesDebug)
  active=nil;index=index+1
  if index==128 then print('PASS native HUD busy consumer:126 pending/header cases preserve both replacements; disabled pending retains native one-packet admission; actual caller returns and borrowed state restored');emu.stop(0)end
 end,emu.callbackType.exec,pc)
end)
emu.addEventCallback(function()emu.setInput({down=frame==80,right=frame==100,start=frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;assert(frame<1000,'Native pending consumer arena completes')end,emu.eventType.endFrame)
