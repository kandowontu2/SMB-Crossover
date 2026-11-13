-- Native controls and bounded read-only observations; no state grants.
local frame,epoch,bits,game,done=0,0,0,false,false
local hold,rearm,attempts,phase=0,0,0,'approach'
local heads,effects,pickups,recent={},{},{},{}
local bestHead=nil
local returns,pending={},nil
local function r(n,i)return emu.read(L[n]+(i or 0),emu.memType.nesDebug)end
local function ram(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function state()return {frame=frame,epoch=epoch,x=x(),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native_state=r('Player_State'),source_state=ram(0x6b),source_y=ram(0x210),engine=r('GameEngineSubroutine'),lives=r('NumberofLives'),status=r('PlayerStatus'),size=r('PlayerSize'),ready=ram(0x8fe),phase=phase}end
local function encode(v)
 if type(v)=='table'then local array,n=true,0;for k in pairs(v)do if type(k)~='number'then array=false end;n=n+1 end;local out={}
  if array then for i=1,n do out[#out+1]=encode(v[i])end;return '['..table.concat(out,',')..']'end
  for k,w in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(w)end;return '{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='nil'then return 'null'else return tostring(v)end
end
local function finish(ok,why)
 if done then return end;done=true;bits=0
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=why,ROM_SHA256=ROM_SHA,controller_only=true,terminal=state(),heads=heads,best_head=bestHead,authored_question_cell=emu.read(0x445,emu.memType.nesDebug),head_effects=effects,pickups=pickups,recent=recent,attempts=attempts}))
 emu.stop(ok and 0 or 1)
end
local function mapped(pc,offset)local m=emu.convertAddress(pc);return m and m.memType==emu.memType.nesPrgRom and m.address==offset end
local function mappedRam(pc,bank)local m=emu.convertAddress(pc);return m and m.memType==emu.memType.nesWorkRam and m.address==bank*8192+(pc&8191)end
local function active()return r('SelectedCharacter')==40 and r('GameEngineSubroutine')==8 and ram(0x8fe)==2 end
local function ground()return r('Player_State')==0 and ram(0x6b)==1 end
local function nearEnemy()
 for i=0,5 do local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x();local id=r('Enemy_ID',i)
  if r('Enemy_Flag',i)==1 and(id==2 or id==6)and r('Enemy_State',i)&32==0 and r('Enemy_Y_Position',i)>=172 and dx>=8 and dx<=30 then return true end
 end;return false
end
local function control()
 if x()<328 then
  if ground()and epoch>=rearm and nearEnemy()then hold=epoch+8;rearm=epoch+47 end
  return 1+(epoch<hold and 128 or 0)
 elseif x()>329 then return 2+(epoch<hold and 128 or 0)end
 phase='question-jump'
 if ground()and epoch>=rearm then
  if attempts>=4 then finish(false,'four-ground-jumps-no-authored-item');return 0 end
  attempts=attempts+1;hold=epoch+8;rearm=epoch+48
 end
 return epoch<hold and 128 or 0
end
emu.addMemoryCallback(function()
 if not game or not active()or not mapped(L.HuHead,HEAD_OFFSET)then return end
 local c=emu.getState();local sp=c['cpu.sp'];local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 pending={pc=pc,sp=(sp+2)&255}
 if not returns[pc]then returns[pc]=true;emu.addMemoryCallback(function()
  if not pending then return end;local c=emu.getState();if c['cpu.pc']~=pending.pc or c['cpu.sp']~=pending.sp then return end
  pending=nil
  if x()>=320 and x()<=352 then local q=state();q.tile=c['cpu.a'];q.row=r('R2');q.fraction=r('R4');q.base=r('R6')+256*r('R7');heads[#heads+1]=q;if #heads>24 then table.remove(heads,1)end;if not bestHead or q.y<bestHead.y then bestHead=q end end
 end,emu.callbackType.exec,pc)end
end,emu.callbackType.exec,L.HuHead)
emu.addMemoryCallback(function()
 if game and mapped(L.NativeRarePlayerHeadCollisionCore,EFFECT_OFFSET)then local q=state();q.tile=emu.getState()['cpu.a'];effects[#effects+1]=q;if #effects>12 then table.remove(effects,1)end end
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
emu.addMemoryCallback(function()
 if not game or not mapped(L.HandlePowerUpCollision,PICKUP_OFFSET)then return end
 local i=emu.getState()['cpu.x'];if i>5 or r('Enemy_ID',i)~=46 or r('Enemy_Flag',i)==0 then return end
 assert(r('InvPickupOwner',i)==40 and r('InvPickup',i)==252,'Original DK native item preparation')
 local q=state();q.slot=i;q.kind=r('PowerUpType',i);q.item_state=r('Enemy_State',i);q.item_x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i);q.item_y=r('Enemy_Y_Position',i)
 pickups[#pickups+1]=q
end,emu.callbackType.exec,L.HandlePowerUpCollision)
local function wait(pred)for _=1,1000 do if pred()then return end;coroutine.yield()end;error('Native readiness bound')end
local function press(pad)bits=pad;for _=1,4 do coroutine.yield()end;bits=0;for _=1,8 do coroutine.yield()end end
local title=coroutine.create(function()
 wait(function()return frame>=70 and emu.read(0x6004,emu.memType.nesDebug)==1 and r('GamePauseStatus')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 end)
 assert(r('CrossoverMenuIndex')==0)
 for _,pad in ipairs({4,4,1,1,1,4})do press(pad)end
 assert(r('CrossoverMenuIndex')==27 and r('SelectedCharacter')==28)
 press(32);assert(r('SelectedCharacter')==40);press(16);wait(active)
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0)
 game=true
end)
if CPU_CONTROLLER_OPENING then frame=541;game=true end
emu.addMemoryCallback(function()
 if game and active()and mappedRam(0xd65e,2)then epoch=epoch+1 end
end,emu.callbackType.exec,0xd65e)
emu.addEventCallback(function()emu.setInput({right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,up=bits&8~=0,start=bits&16~=0,select=bits&32~=0,a=bits&128~=0,b=bits&64~=0},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1
 if game then
  if r('NumberofLives')<2 or r('GameEngineSubroutine')==11 or ram(0x6b)==5 then finish(false,'life-lost');return end
  if #pickups>0 then finish(true,'genuine-native-item-contact');return end
  bits=active()and control()or 0
  if frame%120==0 then recent[#recent+1]=state();if #recent>16 then table.remove(recent,1)end end
  if epoch>1500 or frame>6000 then finish(false,'route-bound')end
 else local ok,why=coroutine.resume(title);assert(ok,why)end
end,emu.eventType.endFrame)
