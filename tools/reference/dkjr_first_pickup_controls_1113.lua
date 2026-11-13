-- Controller-only assisted first mushroom. The ROM owns birth/movement/items.
local function sourceWorldX()return ram(0x213)+8+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function platform()
 for i=0,5 do if r('Enemy_Flag',i)==1 and r('Enemy_ID',i)==37 and r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)==336 then return i end end
end
local function item()
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
  local q={slot=i,state=r('Enemy_State',i),kind=r('PowerUpType',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}
  if not itemBirth then itemBirth={epoch=epoch,frame=frame,actor=q}end
  if q.state&128~=0 and not matureSeen then matureSeen={epoch=epoch,frame=frame,actor=q}end
  return q
 end end
end
local function control()
 if pickupReturn then return 0 end
 local xx,yy=x(),r('Player_Y_Position');local p=platform();local it=item()
 local ride=p and ground()and yy<176 and yy+32==r('Enemy_Y_Position',p)
 if it then
  phase='mushroom-maturity-and-collection'
  if it.state&128==0 or yy<164 then return 0 end
  return xx<it.x-1 and 1 or xx>it.x+1 and 2 or 0
 end
 if xx<344 then
  phase='approach-original-head-column'
  if ground()and epoch>=rearm and nearEnemy()then hold=epoch+8;rearm=epoch+47 end
  return 1+(epoch<hold and 128 or 0)
 elseif xx>345 then return 2 end
 if ride and phase~='rise'and phase~='bump'then phase='rise';released=0;hold=0 end
 if phase=='rise'then
  released=released+1
  if ride and r('Enemy_Y_Position',p)<=180 and released>=4 then phase='bump';hold=epoch+8;attempts=attempts+1 end
 elseif phase~='bump'then
  phase='board'
  if p and ground()and epoch>=rearm and r('Enemy_Y_Position',p)>=192 and r('Enemy_Y_Position',p)<=208 then hold=epoch+8;rearm=epoch+47 end
 end
 return epoch<hold and 128 or 0
end
emu.addMemoryCallback(function()
 if not game or not active()or not mappedRam(0xd1f0,2)then return end
 local i=emu.getState()['cpu.x'];if i>5 then return end
 local left=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)
 if left~=336 then return end
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 assert(i<6 and r('Enemy_ID',i)==37 and r('Enemy_Y_Position',i)==192,'Real new stock helper constructor')
 assert(left-camera>=256 and left-camera<=287,'Offscreen helper admission')
 helperBirths[#helperBirths+1]={slot=i,left=left,center=left+16,initial_top=192,width=32,relative=left-camera,epoch=epoch,frame=frame}
end,emu.callbackType.exec,0xd1f0)
emu.addMemoryCallback(function()
 if not game or not active()or not mapped(L.NrPrepare,PREPARE_OFFSET)then return end
 local i=emu.getState()['cpu.x'];if i>5 or r('Enemy_ID',i)~=46 then return end
 prepared[tostring(i)]={slot=i,kind=r('PowerUpType',i),frame=frame,epoch=epoch}
end,emu.callbackType.exec,L.NrPrepare)
emu.addMemoryCallback(function()
 if not game or not active()or not mappedRam(0xbf6b,3)then return end
 local i=emu.getState()['cpu.x'];assert(i<=5 and r('Enemy_ID',i)==46,'Actual DK owner preparation slot')
 prepared[tostring(i)]={slot=i,kind=r('PowerUpType',i),frame=frame,epoch=epoch,original_owner_prepare=true}
end,emu.callbackType.exec,0xbf6b)
emu.addMemoryCallback(function()
 if not game or not mapped(L.HandlePowerUpCollision,PICKUP_OFFSET)then return end
 local c=emu.getState();local i=c['cpu.x'];if i>5 or r('Enemy_ID',i)~=46 or r('Enemy_Flag',i)==0 then return end
 assert(r('PowerUpType',i)==0 and r('Enemy_State',i)&128~=0,'Mature first mushroom')
 local sp=c['cpu.sp'];local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 pickupPending={pc=pc,sp=(sp+2)&255,slot=i,kind=r('PowerUpType',i)}
 if not pickupReturns[pc]then pickupReturns[pc]=true;emu.addMemoryCallback(function()
  if not pickupPending then return end;local c=emu.getState()
  if c['cpu.pc']~=pickupPending.pc or c['cpu.sp']~=pickupPending.sp then return end
  assert(r('Enemy_Flag',pickupPending.slot)==0,'Actual native item erasure')
  pickupReturn={epoch=epoch,frame=frame,slot=pickupPending.slot,kind=pickupPending.kind,erased=true,status=r('PlayerStatus'),engine=r('GameEngineSubroutine')}
  pickupPending=nil
 end,emu.callbackType.exec,pc)end
end,emu.callbackType.exec,L.HandlePowerUpCollision)
