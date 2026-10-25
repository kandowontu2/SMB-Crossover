-- Explicit rotor-counter seeds at the actual DrawAll boundary. Actors, pose,
-- CHR, OAM, code and CPU execution are left native. Not a gameplay route.
local f,entered,index,pending=0,false,1,nil
local cases={}
for used=4,252,4 do for first=0,used-4,4 do cases[#cases+1]={used,first}end end
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function w(n,v)emu.write(assert(L[n],n),v,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local out=assert(io.open(OUTPUT..'rotor.csv','w'))
out:write('case,used,firstBefore,firstAfter,rotation\n')
emu.addMemoryCallback(function()
 if not entered or r('SelectedCharacter')~=ROTOR_CHARACTER or r('GameEngineSubroutine')~=8 or bank(0xa000)~=B.DrawAllMetasprites then return end
 assert(not pending,'Previous native draw completed')
 pending=cases[index];w('RgOamUsed',pending[1]);w('RgOamFirst',pending[2])
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not pending or bank(0xa000)~=B.DrawAllMetasprites then return end
 out:write(table.concat({index,pending[1],pending[2],r('RgOamFirst'),r('RgOamRotation')},',')..'\n')
 pending=nil;index=index+1
 if index>#cases then out:close();print('PASS2016native rotor boundary cases');emu.stop(0)end
end,emu.callbackType.exec,L.RosterProjectileOamReady)
emu.addEventCallback(function()
 local b={}
 if not entered and f>=60 and f%12==0 then
  if r('CrossoverMenuState')~=2 then b.start=true
  elseif ROTOR_CHARACTER==13 and r('CrossoverMenuIndex')<12 then b.down=true
  elseif r('CrossoverMenuIndex')~=ROTOR_SLOT then b.right=true
  else b.a=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  entered=true;assert(r('SelectedCharacter')==ROTOR_CHARACTER,'Actual menu character entry')
  if ROTOR_CHARACTER==13 then assert(r('KbVariant')==0,'Actual ordinary Kirby menu variant')end
 end
 assert(f<6500,'Bounded native rotor matrix')
end,emu.eventType.endFrame)
