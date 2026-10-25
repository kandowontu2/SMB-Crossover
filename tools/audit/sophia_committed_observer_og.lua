-- Observe completed GameLoop states and the explicitly borrowed block origin.
-- Read-only; the controller stream and captured trace remain untouched.
local frame=0
local out=assert(SOPHIA_LOCK_OUTPUT)
local f=assert(io.open(out..'committed-movement.csv','w'))
f:write('frame,world,level,mode,task,engine,x,y,camera,blockAttack\n')
local b=assert(io.open(out..'borrowed-origin.csv','w'))
b:write('frame,pc,bankA,blockAttack,x,y,savedX,savedY,probeX,probeY,lastDrawX,lastDrawY\n')
local expected,expectedSP=nil,nil
local lastDrawX,lastDrawY=-1,-1
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function bank(a)return emu.convertAddress(a).address//8192 end
emu.addMemoryCallback(function()
 if bank(L.GameLoop)~=B.GameLoop then return end
 assert(not expected,'No nested GameLoop in the canonical movement observer')
 local s=emu.getState();expectedSP=(s['cpu.sp']+2)&255
 expected=(emu.read(0x100+((s['cpu.sp']+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((s['cpu.sp']+2)&255),emu.memType.nesDebug)+1)&0xffff
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function(pc)
 if not expected or pc~=expected then return end
 local s=emu.getState();if s['cpu.sp']~=expectedSP then return end
 expected=nil
 assert(r('MmBlockAttack')==0,'Completed GameLoop restores borrowed projectile/player state')
 f:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),x(),r('Player_Y_Position'),camera(),r('MmBlockAttack')},',')..'\n')
end,emu.callbackType.exec,0,0xffff)
emu.addMemoryCallback(function()
 if bank(L.DrawAllMetasprites)~=B.DrawAllMetasprites then return end
 assert(r('MmBlockAttack')==0,'Actual body drawing never uses the borrowed block origin')
 lastDrawX=x();lastDrawY=r('Player_Y_Position')
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addEventCallback(function()
 frame=frame+1
 if r('MmBlockAttack')==0 or r('OperMode')~=1 then return end
 local s=emu.getState()
 b:write(table.concat({frame,s['cpu.pc'],bank(0xa000),r('MmBlockAttack'),x(),r('Player_Y_Position'),
  r('MmSavedPlayer')+256*r('MmSavedPlayer',1),r('MmSavedPlayer',2),
  (r('MmProbeX')&0xf0)+256*r('MmProbePage'),r('MmProbeY')&0xf0,lastDrawX,lastDrawY},',')..'\n')
end,emu.eventType.endFrame)
local stop=emu.stop
emu.stop=function(code)f:close();b:close();stop(code)end
