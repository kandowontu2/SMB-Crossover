local liftStates,liftMinimum={},255
local liftStart,liftSteps,liftLastY,liftLastUpdate=0,0,nil,nil

local function observeLift()
  if companionUpdates==liftLastUpdate then return end
  liftLastUpdate=companionUpdates
  local state=work(2,STEVE_LIFT_STATE)
  local y=read(0xbd)
  if state>=4 then liftStates[state]=true end
  if state==4 then liftStart=y end
  if state==7 then
    liftMinimum=math.min(liftMinimum,y)
    if liftLastY and y<liftLastY then
      assert(y==liftLastY-1,'Steve rises exactly one pixel per native update')
      liftSteps=liftSteps+1
    end
    local botY=work(2,STEVE_LIFT_BOT_Y)+256*work(2,STEVE_LIFT_BOT_Y+1)
    assert(botY//16==y-12,'The robot moves with Steve during the rise')
  end
  liftLastY=y
end

local function finishLift()
  assert(liftStates[4] and liftStates[5] and liftStates[6] and liftStates[7],
    'Down+A must approach, latch, grip and rise with an earned robot')
  assert(liftStart==48 and liftMinimum==27 and liftSteps==21 and read(0xbd)==48,
    string.format('Lift start %d, peak %d, steps %d, landing %d',liftStart,liftMinimum,liftSteps,read(0xbd)))
  finish(true,string.format('Earned Alpha companion, lifted from Y%d to Y%d and returned, %d rise updates',
    liftStart,liftMinimum,liftSteps))
end
