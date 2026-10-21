-- Real Select-created homing missiles, with isolated vector inputs at the
-- steering boundary. Oracle uses the source's direct cos(atan2)/sin formula.
local updates=0;local slot
local frame=0
local seen={}
local returns,pending={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/70),(frame-550)%70 end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',0x85,11);w('InvSelected',2,11);w('InvAmmo',20,178);w('InvPrevious',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',160);w('Enemy_PageLoc',0);w('Enemy_Y_Position',112);w('Enemy_Y_HighPos',1)
 w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',255);w('MmEnemyHealthHi',127);w('AvStopwatch',200)
end

L.R0=3;L.R1=4;L.R2=5;L.R3=6
local operands,checked=0,0
local vectorCalls=0
local products={}
emu.addMemoryCallback(function()
 if frame<550 or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) then return end
 vectorCalls=vectorCalls+1
 local s=r('AvSlot');w('RgShotX',68,s);w('RgShotPage',0,s);w('RgShotY',28,s);w('RgShotYHigh',1,s)
end,emu.callbackType.exec,assert(L.SophiaHomingVector))
emu.addMemoryCallback(function()
 if frame<550 or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) or operands>=65536 then return end
 assert(emu.read(L.SophiaByteProductOperands,emu.memType.nesDebug)==0xa5 and emu.read(L.SophiaByteProductOperands+1,emu.memType.nesDebug)==4,'Pinned native scratch operands R0=3,R1=4')
 local a,b=operands%256,operands//256
 operands=operands+1
 w('R0',a);w('R1',b)
 local sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 pending={sp=sp,a=a,b=b}
 if products[pc]then return end
 products[pc]=true
 emu.addMemoryCallback(function()
  if not pending or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) or emu.getState()['cpu.sp']~=pending.sp+2 then return end
  local p=pending;pending=nil
  local actual=r('R2')+256*r('R3')
  assert(actual==p.a*p.b,'Native quarter-square product '..p.a..'*'..p.b..' got '..actual)
  checked=checked+1
  if checked==65536 then print('PASS all65536 native Sophia quarter-square products match independent integer multiplication');emu.stop(0)end
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaByteProductOperands))
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=frame>=562 and frame<600 and frame%8>=2 and frame%8<5},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then fixture()end
 if frame>=550 then w('AvStopwatch',200)end
 if frame==650 then assert(r('SelectedCharacter')==11,'Real menu selects Sophia');assert(vectorCalls>0,'Actual Select missiles reach steering: ammo='..r('InvAmmo',178)..' engine='..r('GameEngineSubroutine')..' task='..r('OperMode_Task')..' status='..r('PlayerStatus')..' owned='..r('InvOwnedLo',11)..' state='..r('Player_State'))end
 if frame==15000 then assert(false,'Native product exhaustive run completed: '..checked)end
end,emu.eventType.endFrame)
