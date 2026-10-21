-- Diagnostic only: the common fixture authors a flat arena and actual enemy
-- body contact. This observer never changes injury state, control flow or time.
-- Pinned 2.02 expects80Flashpx/s recoil for450ms, not native shrink freeze.
BODY_CHARACTER=INJURY_CHARACTER or 1
BODY_FIRST=5;BODY_LAST=5
local tick,phase,facing,origin,observed,diverged=0,nil,nil,nil,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function x()return r('Player_PageLoc')*256+r('Player_X_Position')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local out=assert(io.open(OUTPUT..ROM_NAME..'-injury-probe-'..BODY_CHARACTER..'.csv','w'))
out:write('tick,age,facing,x,source_x,vx,source_vx,vy,engine,timer,invulnerability\n')
emu.addMemoryCallback(function()
 if tick>=550 then phase=0;facing=r('PlayerFacingDir');origin=x()end
end,emu.callbackType.exec,L.ForceInjury)
emu.addEventCallback(function()
 tick=tick+1
 if not phase then return end
 local recoil=phase<27 and(facing==1 and-80/120 or 80/120)or 0
 local expected=origin+(facing==1 and-1 or 1)*math.min(phase,27)*80/120
 local actual=x()
 out:write(table.concat({tick,phase,facing,actual,expected,q('MmVX'),recoil,q('MmVY'),r('GameEngineSubroutine'),r('TimerControl'),r('InjuryTimer')},',')..'\n')
 if phase==2 then
  observed=observed+1
  if math.abs(q('MmVX')-recoil)>.02 then diverged=diverged+1 end
  print('INJURY_BASELINE char'..BODY_CHARACTER..' facing'..facing..' sourceVX'..recoil..' actualVX'..q('MmVX')..' engine'..r('GameEngineSubroutine')..' nativeTimer'..r('TimerControl'))
 end
 phase=phase+1
 if observed==2 and phase==45 then
  out:close();assert(diverged==2,'This diagnostic must reproduce both native freeze negatives on the baseline')
  print('PASS diagnostic preserves two source injury negatives; no injury-fidelity acceptance claimed')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
dofile(TEST_DIR..'megaman-bass-body-contact-202.lua')
