-- Observe shots already in flight while the earned robot begins a lift.
local liftProjectilePending,liftProjectileTiles={},{}
local liftProjectileFrames=0
emu.addMemoryCallback(guard(function(_,value)
  if value~=2 or phase~='companion-route' then return end
  local state=work(2,STEVE_LIFT_STATE)
  if state<4 or state>7 then return end
  liftProjectileFrames=liftProjectileFrames+1
  for at=0,252,4 do
    local y,tile=read(0x200+at),read(0x201+at)
    if y<240 and (tile==0x77 or tile==0x79) then
      liftProjectilePending[#liftProjectilePending+1]={at,y,tile,read(0x202+at),read(0x203+at)}
    end
  end
end),emu.callbackType.write,0x4014)
local function observeLiftProjectile()
  for _,cell in ipairs(liftProjectilePending) do
    for i=1,4 do
      assert(emu.read(cell[1]+i-1,emu.memType.nesSpriteRam)==cell[i+1],
        'Live lift projectile reaches physical OAM')
    end
    liftProjectileTiles[cell[3]]=true
  end
  liftProjectilePending={}
end
