-- Authored RAM arenas at the actual ordinary-enemy JSR. No PC/register/ROM
-- patches, state loads or level-clear claims. Compare the resulting CSV with
-- the immutable native-helper control; the standalone unit also checks RAM.
local frame,depth,index,current,actor=0,0,0,nil,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function foreground()return depth==0 and r('CurrentBank')%128==0 end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced bbox interrupts')end,emu.callbackType.exec,assert(pc))end
local out=assert(io.open(OUTPUT..ROM_NAME..'-bbox-caller.csv','w'))
out:write('case,slot,left,world,relative,y,offscreen,box,A,X,Y,P,SP,R0,R1,R2,R3,R4,R5,R6,R7,masked,ulx,uly,lrx,lry\n')
local cases={}
for _,left in ipairs({0,255,65408})do
 for _,relative in ipairs({-1,0,1,127,128,255,256})do
  for _,bits in ipairs({0,1,4,8,0x44,0x48,255})do
   for _,box in ipairs({0,1,8,9,10,11})do
    for slot=0,5 do cases[#cases+1]={slot=slot,left=left,world=(left+relative)&65535,relative=(relative+256)&255,y=({0,31,32,184,223,255})[slot+1],bits=bits,box=box}end
   end
  end
 end
end
local function stableActor(slot)
 w('Enemy_PageLoc',1,slot);w('Enemy_X_Position',80+24*slot,slot);w('Enemy_Y_Position',184,slot);w('Enemy_Y_HighPos',1,slot)
 w('Enemy_X_Speed',8,slot);w('Enemy_Y_Speed',0,slot);w('Enemy_X_MoveForce',0,slot);w('Enemy_Y_MoveForce',0,slot)
 w('Enemy_State',0,slot);w('Enemy_MovingDir',1,slot);w('Enemy_CollisionBits',0,slot);w('Enemy_BoundBoxCtrl',9,slot);w('EnemyOffscrBitsMasked',0,slot)
 local b=slot*4;w('EnemyBoundingBoxCoord',83+24*slot,b);w('EnemyBoundingBoxCoord',198,b+1);w('EnemyBoundingBoxCoord',93+24*slot,b+2);w('EnemyBoundingBoxCoord',204,b+3)
end
local returns={}
emu.addMemoryCallback(function()
 if frame<550 or not foreground()then return end
 assert(not actor,'Previous actual native bbox actor returned')
 local s=emu.getState();local sp=s['cpu.sp']
 actor={slot=s['cpu.x'],sp=(sp+2)&255,ret=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535}
 local ret=actor.ret
 if not returns[ret]then returns[ret]=true;emu.addMemoryCallback(function()
  if not actor or not foreground()or emu.getState()['cpu.sp']~=actor.sp then return end
  assert(actor.tested,'Every actual native actor reaches the scoped bbox helper')
  assert(r('Enemy_X_MoveForce',actor.slot)==128,'Native Goomba movement continues exactly once')
  actor=nil
 end,emu.callbackType.exec,ret)end
end,emu.callbackType.exec,assert(L.RunEnemyObjectsCore))
local helper=L.NormalEnemyBoundBox or assert(L.GetEnemyBoundBox)
emu.addMemoryCallback(function()
 if frame<550 or not foreground()then return end
 assert(actor and not current,'Coherent native bbox caller')
 index=index+1;current=cases[index]
 if not current then out:close();print('PASS '..#cases..' actual bbox caller arenas, all6 native slots, masked fallback and zero bits, real continued AI');emu.stop(0);return end
 local c=current;local s=emu.getState();assert(s['cpu.x']==c.slot,'Sequential actual native slots')
 local sp=s['cpu.sp'];c.sp=(sp+2)&255;c.ret=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 assert(c.ret==L.RunNormalEnemies+17,'Scoped actual JSR after native graphics')
 for i=0,7 do w('R0',(i*37+index*13)&255,i)end
 w('ObjectOffset',c.slot);w('ScreenLeft_X_Pos',c.left);w('ScreenLeft_PageLoc',c.left>>8)
 w('Enemy_X_Position',c.world,c.slot);w('Enemy_PageLoc',c.world>>8,c.slot)
 w('Enemy_Rel_XPos',c.relative);w('Enemy_Rel_YPos',c.y);w('Enemy_BoundBoxCtrl',c.box,c.slot);w('Enemy_OffscreenBits',c.bits)
 if not returns[c.ret]then returns[c.ret]=true;emu.addMemoryCallback(function()
  if not current or not foreground()or emu.getState()['cpu.sp']~=current.sp then return end
  local q=current;local cpu=emu.getState();assert(cpu['cpu.x']==q.slot,'BBox preserves actual native slot')
  local row={index,q.slot,q.left,q.world,q.relative,q.y,q.bits,q.box,cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps'],cpu['cpu.sp']}
  for i=0,7 do row[#row+1]=r('R0',i)end
  row[#row+1]=r('EnemyOffscrBitsMasked',q.slot)
  for i=0,3 do row[#row+1]=r('EnemyBoundingBoxCoord',q.slot*4+i)end
  out:write(table.concat(row,',')..'\n')
  -- Keep the real caller coherent after the isolated geometry input, without
  -- changing any CPU registers, so its native terrain/collision/AI still runs.
  stableActor(q.slot);w('Enemy_OffscreenBits',0);w('Enemy_Rel_XPos',80+24*q.slot);w('Enemy_Rel_YPos',184)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1)
  actor.tested=true;current=nil
 end,emu.callbackType.exec,c.ret)end
end,emu.callbackType.exec,helper)
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240,right=frame==80},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==1 and r('GameEngineSubroutine')==8,'Real menu launches bbox unit arena')
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
 assert(frame<6000,'Bounded actual bbox matrix '..index..'/'..#cases)
end,emu.eventType.endFrame)
