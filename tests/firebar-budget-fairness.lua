-- Render-only dense native-object arena. Restore all authored fields at the
-- actual DrawAllMetasprites return; no OAM/CPU/ROM/hardware writes.
local frame,depth,index=0,0,0
local active,hooks=nil,{}
local lastComplete,dma,closing=nil,nil,nil
local dmaChecks=0
local eligible={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local complete={0,0,0};local visible={0,0,0}
local function bytes()
 local s={};for i=0,255 do s[#s+1]=string.char(r('Sprite_Data',i))end;return table.concat(s)
end
local function put(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function w(n,v,i)
 local addr=assert(L[n],n)+(i or 0)
 if active.old[addr]==nil then active.old[addr]=emu.read(addr,emu.memType.nesDebug)end
 emu.write(addr,v&255,emu.memType.nesDebug)
end
local out=assert(io.open(OUTPUT..ROM_NAME..'-firebar-budget.csv','w'))
out:write('pass,frame,short2,short3,long4,usedOffset,cyclesIncludingInterrupts\n')
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0)end,emu.callbackType.exec,assert(pc))end
local function returned(pc)
 if not active or depth~=0 or active.pc~=pc then return end
 local st=emu.getState();if st['cpu.sp']~=(active.sp+2)%256 then return end
 assert(active.admitted==1,'Exactly one firebar turn per complete object list')
 for _,object in ipairs({1,2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21})do
  assert(active.visited[object]==1,'Every ordinary object retains exactly one draw turn: '..object)
 end
 local found={0,0,0}
 for i=0,63 do
  local at=i*4;local y=r('Sprite_Y_Position',at);local x=r('Sprite_X_Position',at);local tile=r('Sprite_Tilenumber',at)
  if y<240 and(tile==0x41 or tile==0x43 or tile==0x40 or tile==0x42)and(r('Sprite_Attributes',at)&3)==2 then
   for b,bx in ipairs({48,112,176})do if x==bx and y>=60 and y<=148 and(y-60)%8==0 then found[b]=found[b]+1 end end
  end
 end
 for b,n in ipairs({6,6,12})do
  if found[b]>0 then visible[b]=visible[b]+1 end
  if found[b]==n then complete[b]=complete[b]+1 end
 end
 local cycle=st['cpu.cycleCount']or st['cpu.cycle']
 out:write(table.concat({index,frame,found[1],found[2],found[3],r('RgOamUsed'),cycle-active.cycle},',')..'\n');out:flush()
 lastComplete={bytes=bytes(),index=index}
 for addr,v in pairs(active.old)do emu.write(addr,v,emu.memType.nesDebug)end
 active=nil
 if index==64 then
  closing=frame+5
 end
end
emu.addMemoryCallback(function()
 if frame<600 or closing or depth~=0 or r('CurrentBank')%128~=4 then return end
 assert(not active,'Previous complete draw returned before another arena')
 local st=emu.getState();local sp=st['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 active={old={},sp=sp,pc=pc,visited={},admitted=0,cycle=st['cpu.cycleCount']or st['cpu.cycle']};index=index+1
 if not hooks[pc]then hooks[pc]=true;emu.addMemoryCallback(function()returned(pc)end,emu.callbackType.exec,pc)end
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
 for i=1,23 do w('ObjectMetasprite',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_ID',0,i);w('FirebarPartCount',0,i);w('EnemyVerticalFlip',0,i)end
 for i=0,1 do
  w('Enemy_Flag',i==0 and 1 or 128,i);w('Enemy_ID',0x2d,i)
  w('EnemyMetasprite',i==0 and L.METASPRITE_BOWSER_FRONT_MOUTH_OPEN or L.METASPRITE_BOWSER_REAR_WALK_1,i)
  w('Enemy_X_Position',208+i*16,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',144,i);w('Enemy_Y_HighPos',1,i);w('Enemy_MovingDir',1,i);w('Enemy_SprAttrib',0,i)
 end
 for b,slot in ipairs({2,3,4})do
  w('Enemy_Flag',1,slot);w('Enemy_ID',slot==4 and 0x1f or 0x1b,slot);w('FirebarPartCount',slot==4 and 12 or 6,slot)
  for part=0,(slot==4 and 11 or 5)do w('FirebarPartX',({48,112,176})[b],slot*12+part);w('FirebarPartY',64+part*8,slot*12+part)end
 end
 w('Enemy_Flag',132,5);w('Enemy_ID',0x1f,5)
 for i=0,8 do
  w('MiscMetasprite',L.METASPRITE_HAMMER_FRAME_2,i);w('Misc_X_Position',8+i*24,i);w('Misc_PageLoc',0,i);w('Misc_Y_Position',96,i);w('Misc_Y_HighPos',1,i)
 end
 for i=0,3 do w('BlockMetasprite',L.METASPRITE_MISC_BRICK_GROUND,i);w('Block_X_Position',16+i*48,i);w('Block_PageLoc',0,i);w('Block_Y_Position',192,i);w('Block_Y_HighPos',1,i)end
 for i=0,1 do w('FireballMetasprite',L.METASPRITE_FIREBALL_FRAME_1,i);w('Fireball_X_Position',32+i*160,i);w('Fireball_PageLoc',0,i);w('Fireball_Y_Position',128,i);w('Fireball_Y_HighPos',1,i)end
 for i=0,9 do w('RgShotType',1,i);w('RgShotX',24+i*20,i);w('RgShotPage',0,i);w('RgShotY',48,i);w('RgShotYHigh',1,i);w('RgShotAge',1,i)end
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if active and depth==0 and r('CurrentBank')%128==4 then
  local obj=emu.getState()['cpu.y'];active.visited[obj]=(active.visited[obj]or 0)+1
 end
end,emu.callbackType.exec,L.DrawMetasprite)
emu.addMemoryCallback(function()
 if active and depth==0 and r('CurrentBank')%128==4 then active.admitted=active.admitted+1 end
end,emu.callbackType.exec,L.WorldFirebarAdmission)
emu.addMemoryCallback(function(_,page)
 if not lastComplete then return end
 local s={};for i=0,255 do s[#s+1]=string.char(emu.read(page*256+i,emu.memType.nesDebug))end
 local payload=table.concat(s)
 if payload==lastComplete.bytes then dma={bytes=payload,index=lastComplete.index}else dma=nil end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if dma then
  local actual={};for i=0,255 do actual[#actual+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
  assert(table.concat(actual)==dma.bytes,'Actual hardware sprite RAM matches the completed dense sprite list')
  local raw=dma.bytes;local lines={}
  local state=ROM_NAME:find('mmc5')and emu.getState()or nil
  local function chr(a)
   if state then return emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)end
   return emu.read(a,emu.memType.nesPpuDebug)
  end
  for s=0,63 do
   local at=s*4;local y=raw:byte(at+1);local tile=raw:byte(at+2);local pal=raw:byte(at+3);local x=raw:byte(at+4)
   if y<240 then
    local admitted=false
    for yy=y+1,math.min(239,y+16)do
     if(lines[yy]or 0)<8 then
      local row=yy-y-1;if pal&128~=0 then row=15-row end
      local a=(tile&1)*4096+(tile&254)*16+(row//8)*16+row%8
      if chr(a)|chr(a+8)~=0 then admitted=true end
     end
     lines[yy]=(lines[yy]or 0)+1
    end
    if admitted and(tile==0x41 or tile==0x43 or tile==0x40 or tile==0x42)and pal&3==2 then
     for b,bx in ipairs({48,112,176})do
      local part=(y-60)//8
      if x==bx and(y-60)%8==0 and part>=0 and part<({6,6,12})[b]then eligible[b..':'..part]=true end
     end
    end
   end
  end
  dmaChecks=dmaChecks+1;dma=nil
 end
 if closing and frame>=closing then
  out:close()
  for b,n in ipairs(complete)do assert(n>0,'Dense scene must not permanently omit firebar'..b..'; complete='..n..' visible='..visible[b])end
  assert(dmaChecks>=16,'Dense completed lists reach actual hardware sprite RAM')
  for b,n in ipairs({6,6,12})do for p=0,n-1 do assert(eligible[b..':'..p],'Each firebar part receives hardware scanline eligibility within the observation window: '..b..':'..p)end end
  print('PASS64 dense completed sprite lists and '..dmaChecks..' actual DMA checks: each ordinary object keeps one turn; all3 firebars receive complete OAM allocation; all24 parts get a nontransparent sprite row within the hardware scanline limit; complete '..table.concat(complete,':')..' visible '..table.concat(visible,':'))
  emu.stop(0)
 end
 if frame==650 or frame==690 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-firebar-budget-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if frame==199 then put('LevelNumber',3);put('AreaNumber',4)end
 assert(frame<1500,'Bounded dense rendering regression')
end,emu.eventType.endFrame)
