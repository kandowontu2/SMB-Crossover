-- Isolated actual-native-caller ABI arenas, not controller traversal evidence.
-- Only authored RAM is seeded. No CPU registers, PC, ROM, OAM or states are
-- patched. After observing the helper return, restore coherent actor/viewport
-- RAM before continuing the real Goomba graphics/collision/AI caller.
local frame,depth,index,current,actor,repair=0,0,0,nil,nil,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function foreground()return depth==0 and r('CurrentBank')%128==0 end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced offscreen interrupts')end,emu.callbackType.exec,assert(pc))end
local out=assert(io.open(OUTPUT..ROM_NAME..'-offscreen-caller.csv','w'))
out:write('case,slot,left,right,world,y,high,objectOffset,A,X,Y,P,SP,R0,R1,R2,R3,R4,R5,R6,R7,offscreen\n')
local cases={}
local function append(left,width,relative,y,hi)
 for slot=0,5 do cases[#cases+1]={slot=slot,left=left,right=(left+width)&65535,world=(left+relative)&65535,y=y,hi=hi}end
end
for _,left in ipairs({0,255,256,65408})do for _,width in ipairs({23,24,127,239,255,256})do for _,relative in ipairs({-257,-256,-1,0,1,23,24,55,56,127,231,232,255,256,257})do append(left,width,relative,184,1)end end end
for _,y in ipairs({0,1,7,8,31,32,64,127,128,184,223,224,248,255})do for _,hi in ipairs({0,1,2,127,128,255})do for _,relative in ipairs({1,231,232})do append(65407,255,relative,y,hi)end end end

local function subtract(a,b,carry)
 local z=a-b-(1-carry);local v=z&255
 return v,z>=0 and 1 or 0,((a~b)&(a~v)&128)~=0 and 1 or 0
end
local function reference(c,ps,scratch)
 -- Independent source equations, including scratch writes made only by some
 -- branches. This is not a restatement of the candidate interior predicate.
 local regs={table.unpack(scratch)};local xbits,ybits,overflow
 local xt={0x7f,0x3f,0x1f,0x0f,7,3,1,0,0x80,0xc0,0xe0,0xf0,0xf8,0xfc,0xfe,0xff}
 for side=1,0,-1 do
  local edge=side==1 and c.right or c.left
  local low,carry=subtract(edge&255,c.world&255,1)
  local high;high,carry,overflow=subtract((edge>>8)&255,(c.world>>8)&255,carry)
  regs[8]=low
  local k=side==1 and 15 or 7
  if high<128 then
   k=side==1 and 7 or 15
   if high<1 then
    regs[7]=56;regs[6]=8
    if low<56 then k=(low>>3)&7;if side==0 then k=k+8;overflow=0 end end
   end
  end
  xbits=xt[k+1];if xbits~=0 then break end
 end
 local yt={0,8,12,14,15,7,3,1,0}
 for side=1,0,-1 do
  local low,carry=subtract(side==1 and 0 or 255,c.y,1)
  local high;high,carry,overflow=subtract(1,c.hi,carry)
  regs[8]=low
  local k=side==1 and 0 or 4
  if high<128 then
   k=side==1 and 4 or 0
   if high<1 then
    regs[7]=32;regs[6]=4
    if low<32 then k=(low>>3)&7;if side==0 then k=k+4;overflow=0 end end
   end
  end
  ybits=yt[k+1];if ybits~=0 then break end
 end
 local bits=(xbits>>4)|((ybits<<4)&255)
 regs[1]=bits;regs[5]=c.slot+1
 local flags=(ps&(~0xc3))|(c.offset&128)|(c.offset==0 and 2 or 0)|(overflow<<6)
 return bits,flags,regs
end
local function stableActor(slot)
 w('Enemy_PageLoc',1,slot);w('Enemy_X_Position',80+24*slot,slot);w('Enemy_Y_Position',184,slot);w('Enemy_Y_HighPos',1,slot)
 w('Enemy_X_Speed',8,slot);w('Enemy_Y_Speed',0,slot);w('Enemy_X_MoveForce',0,slot);w('Enemy_Y_MoveForce',0,slot)
 w('Enemy_State',0,slot);w('Enemy_MovingDir',1,slot);w('Enemy_CollisionBits',0,slot);w('Enemy_BoundBoxCtrl',9,slot);w('EnemyOffscrBitsMasked',0,slot)
end
local returns={};local helper=L.NormalEnemyOffscreenBits or assert(L.GetEnemyOffscreenBits)
emu.addMemoryCallback(function()
 if frame<550 or not foreground()then return end
 assert(not actor,'Previous actual native AI caller returned')
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 actor={slot=cpu['cpu.x'],sp=(sp+2)&255,ret=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535}
 local ret=actor.ret
 if not returns[ret]then returns[ret]=true;emu.addMemoryCallback(function()
  if not actor or not foreground()or emu.getState()['cpu.sp']~=actor.sp then return end
  assert(actor.tested,'Every actual actor reached the scoped helper')
  assert(r('Enemy_X_MoveForce',actor.slot)==128,'Unmodified native Goomba movement executes once after restored unit arena')
  actor=nil
 end,emu.callbackType.exec,ret)end
end,emu.callbackType.exec,assert(L.RunEnemyObjectsCore))
emu.addMemoryCallback(function()
 if frame<550 or not foreground()then return end
 assert(actor and not current and repair==nil,'Coherent ordinary-enemy caller before helper')
 index=index+1;current=cases[index]
 if not current then out:close();print('PASS '..#cases..' actual offscreen caller ABI arenas, all6 slots, accepted/rejected edges/pages/Y, unusual ObjectOffset, exact registers/flags/scratch/SP and continued native AI');emu.stop(0);return end
 assert(emu.getState()['cpu.x']==current.slot,'Every authored geometry reaches all6 real native slots')
end,emu.callbackType.exec,assert(L.RunNormalEnemies))
emu.addMemoryCallback(function()
 if not current or not foreground()then return end
 local c=current;local cpu=emu.getState();assert(cpu['cpu.x']==c.slot,'Actual helper input X')
 local sp=cpu['cpu.sp'];c.sp=(sp+2)&255;c.ret=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 c.offset=({c.slot,5-c.slot,0,5,127,128,255})[(index-1)%7+1]
 for i=0,7 do w('R0',(i*37+index*13)&255,i)end
 w('ObjectOffset',c.offset);w('ScreenLeft_X_Pos',c.left);w('ScreenLeft_PageLoc',c.left>>8);w('ScreenRight_X_Pos',c.right);w('ScreenRight_PageLoc',c.right>>8)
 w('Enemy_X_Position',c.world,c.slot);w('Enemy_PageLoc',c.world>>8,c.slot);w('Enemy_Y_Position',c.y,c.slot);w('Enemy_Y_HighPos',c.hi,c.slot)
 local scratch={};for i=0,7 do scratch[#scratch+1]=r('R0',i)end
 c.bits,c.ps,c.scratch=reference(c,cpu['cpu.ps'],scratch)
 if not returns[c.ret]then returns[c.ret]=true;emu.addMemoryCallback(function()
  if not current or not foreground()or emu.getState()['cpu.sp']~=current.sp then return end
  local q=current;local s=emu.getState()
  assert(s['cpu.a']==q.bits and s['cpu.x']==q.offset and s['cpu.y']==1 and s['cpu.ps']==q.ps,'Exact actual helper A/X/Y/all flags: case'..index)
  local row={index,q.slot,q.left,q.right,q.world,q.y,q.hi,q.offset,s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp']}
  for i=0,7 do assert(r('R0',i)==q.scratch[i+1],'Exact source scratch R'..i..' case'..index);row[#row+1]=r('R0',i)end
  assert(r('Enemy_OffscreenBits')==q.bits,'Exact shared native offscreen result');row[#row+1]=r('Enemy_OffscreenBits');out:write(table.concat(row,',')..'\n')
  -- Restore authored coherent RAM, leaving CPU registers/stack untouched.
  w('ObjectOffset',q.slot);stableActor(q.slot);w('Enemy_OffscreenBits',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1)
  actor.tested=true;repair=q.slot;current=nil
 end,emu.callbackType.exec,c.ret)end
end,emu.callbackType.exec,helper)
emu.addMemoryCallback(function()
 if repair==nil or not foreground()then return end
 assert(emu.getState()['cpu.x']==repair,'Native relative routine restores the real ObjectOffset')
 w('Enemy_Rel_XPos',80+24*repair);w('Enemy_Rel_YPos',184);repair=nil
end,emu.callbackType.exec,assert(L.EnemyGraphicsEngine))
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240,right=frame==80},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==1 and r('GameEngineSubroutine')==8,'Real menu launches offscreen unit arena')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',1,i);w('Enemy_ID',6,i);stableActor(i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,3 do w('MmBulletType',0,i)end
  for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('MmVX',0,i);w('MmVY',0,i)end
  w('Player_X_Position',8);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',3)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('HorizontalScroll',0);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyObjectPageLoc',255)
  w('AvStopwatch',0);w('TimerControl',0);w('InjuryTimer',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0);w('MmDeathFlag',0);w('PlayerOutlinesOff',1)
 end
 assert(frame<4000,'Bounded actual offscreen caller matrix '..index..'/'..#cases)
end,emu.eventType.endFrame)
