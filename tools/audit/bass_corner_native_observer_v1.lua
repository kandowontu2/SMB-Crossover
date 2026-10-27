-- Passive bounded Bass head/wall observations. Static bank-qualified
-- hooks; no dynamic callbacks, dumps, state writes, or input changes.
return function(out)
 local f=assert(io.open(out..'bass-collision.csv','w'))
 f:write('frame,call,phase,cycle,x,y,fraction_y,vy_q16,state,body,ceiling,block_row,tile,nmi_disable\n')
 local frame,calls,rows,active=0,0,0,false
 local totals={heads=0,post_ceiling=0,walls=0,bg_calls=0,max_bg_cycles=0}
 local start
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(pc)return emu.convertAddress(pc).address//8192 end
 local function owned()
  return r('SelectedCharacter')==9 and r('RlVariant')==0 and r('OperMode')==1 and
   r('GameEngineSubroutine')==8 and r('WorldNumber')==0 and r('LevelNumber')==0
 end
 local function log(phase)
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  if x<280 or x>460 then return end
  rows=rows+1;assert(rows<=12000,'Bounded Bass collision observations')
  local vy=r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2);if vy>=0x800000 then vy=vy-0x1000000 end
  f:write(table.concat({frame,calls,phase,emu.getState()['cpu.cycleCount'],x,r('Player_Y_Position'),
   r('MmYFraction')+256*r('MmYFraction',1),vy,r('Player_State'),r('Player_BoundBoxCtrl'),
   r('SmCeilingHit'),r('R2'),r('R3'),r('NmiDisable')},',')..'\n')
 end
 local function hook(name,fn)
  local pc=assert(L[name],name);local expected=assert(B[name],name..' bank')
  emu.addMemoryCallback(function()if bank(pc)==expected and owned()then fn()end end,emu.callbackType.exec,pc)
 end
 hook('PlayerBGCollision',function()
  calls=calls+1;totals.bg_calls=calls;active=true;start=emu.getState()['cpu.cycleCount'];log('before-BG')
 end)
 hook('SamusAfterBGCollisionBridge',function()
  if active then totals.post_ceiling=totals.post_ceiling+1;log('native-head-response')end
 end)
 hook('MegaMan202AfterBG',function()
  if active then
   totals.max_bg_cycles=math.max(totals.max_bg_cycles,emu.getState()['cpu.cycleCount']-start)
   log('after-BG');active=false
  end
 end)
 hook('SamusStopAtWallBanked',function()totals.walls=totals.walls+1;if active then log('wall')end end)
 if L.BassHeadProbe then hook('BassHeadProbe',function()totals.heads=totals.heads+1;log('head-probe')end)end
 emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
 return function()f:close();return totals end
end
