-- An actual cold-boot controller route collects a mushroom, takes an enemy
-- hit, reaches 1-1's pole, then enters 1-2. No memory/register/ROM writes.
-- The old build leaves PlayerChangeSizeFlag=1 after its injury at frame 3131
-- and sticks on the pole at (3161,136) forever. This is separate from arenas.
local inputs={}
for line in io.lines(TEST_DIR..'fixtures/samus-injury-flagpole-inputs.csv')do
 local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
 if p then inputs[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)}end
end
local frame,poll=0,0
local powered,hurt,pole,nextStart=false,false,false,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addEventCallback(function()
 poll=poll+1
 local b={}
 if nextStart then b.right=true
 else
  local input=assert(inputs[poll],'Controller prefix exhausted')
  assert(input.frame==frame,'Controller poll/frame remains synchronized')
  for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[name]=(input.mask&bit)>0 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>540 then
  assert(r('SelectedCharacter')==2,'Samus chosen through the real menu')
  if r('PlayerStatus')>0 then powered=true end
  if r('GameEngineSubroutine')==10 then hurt=true end
  if hurt and r('GuestPowerupActive')==0 then
   assert(r('PlayerChangeSizeFlag')==0,'Guest injury never leaves a native shrink flag that blocks scripted movement')
  end
  if r('GameEngineSubroutine')==4 then pole=true end
  if r('LevelNumber')==1 and r('GameEngineSubroutine')==8 then
   local x=r('Player_X_Position')+256*r('Player_PageLoc')
   if not nextStart then nextStart={frame=frame,x=x}
   elseif frame>=nextStart.frame+25 then
    assert(powered and hurt and pole,'Real mushroom, native enemy injury and pole contact precede 1-2')
    assert(x>nextStart.x+5,'Samus moves normally after the native 1-2 entrance')
    print('PASS controller-only Samus mushroom, enemy injury, 1-1 pole/castle and 1-2 control without stale shrink state');emu.stop(0)
   end
  end
 end
 if frame==6000 then assert(false,'Injured Samus flagpole watchdog: engine '..r('GameEngineSubroutine')..' level '..r('LevelNumber')..' y '..r('Player_Y_Position'))end
end,emu.eventType.endFrame)
