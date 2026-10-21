-- Real Select-created homing missiles, with isolated vector inputs at the
-- steering boundary. Oracle uses the source's direct cos(atan2)/sin formula.
local cases={{100,0},{-100,0},{0,100},{0,-100},{48,64},{64,48},{-48,64},{48,-64},{-48,-64},{-64,48},{64,-48},{-64,-48},{9,200},{200,9},{1,200},{200,1},{200,200},{-200,-200}}
local original=#cases;for i=1,original do cases[#cases+1]={cases[i][1],cases[i][2],512}end
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
emu.addMemoryCallback(function()
 local n=phase()
 if n<0 or n>=#cases or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) then return end
 local slot=r('AvSlot');local target=r('SsMode',slot)
 local dx,dy=table.unpack(cases[n+1]);local sx,sy=168-dx,384-dy
 w('RgShotX',sx,slot);w('RgShotPage',math.floor(sx/256),slot);w('RgShotY',sy,slot);w('RgShotYHigh',math.floor(sy/256),slot)
 w('Enemy_X_Position',160,target);w('Enemy_PageLoc',0,target);w('Enemy_Y_Position',112,target);w('Enemy_Y_HighPos',1,target)
 for _,field in ipairs({'RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi'})do w(field,0,slot)end
 local force=cases[n+1][3]or 128;w('AvTmp2',force%256);w('AvSavedY',force//256)
 local sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 pending={n=n,slot=slot,sp=sp}
 if returns[pc]then return end
 returns[pc]=true
 emu.addMemoryCallback(function()
  if not pending or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) or emu.getState()['cpu.sp']~=pending.sp+2 then return end
  local p=pending;pending=nil;local dx,dy=table.unpack(cases[p.n+1]);local length=math.sqrt(dx*dx+dy*dy);local force=cases[p.n+1][3]or 128
  local vx=r('RgShotVXLo',p.slot)+256*r('RgShotVXHi',p.slot);if vx>=32768 then vx=vx-65536 end
  local vy=r('RgShotVYLo',p.slot)+256*r('RgShotVYHi',p.slot);if vy>=32768 then vy=vy-65536 end
  assert(math.abs(vx-force*dx/length)<=4 and math.abs(vy-force*dy/length)<=4,'Source normalized homing vector '..dx..','..dy..' actual='..vx..','..vy)
  seen[p.n+1]=true
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaHomingProject,'Source normalized vector projection'))
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=n>=0 and n<#cases and t>=12 and t<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==#cases then print('PASS source normalized homing acceleration: '..#cases..' cardinal/diagonal/steep/seam cases within nativeQ8.8 precision');emu.stop(0);return end
 if t==0 then fixture()end
 if t==65 then assert(seen[n+1],'Actual homing shot exercises source vector '..n)end
end,emu.eventType.endFrame)
