-- Ice Climber has a short, locked air trajectory. Approach actual pit edges;
-- the broad Mario controller's32px lookahead launches it too early.
local root=ROSTER_CONFIG.root
local original=dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')
local lastX,still=0,0
return function(c)
 local b=original(c)
 if c.char~=20 or c.world~=0 or c.level~=0 or c.x<450 then return b end
 local function solid(wx,y)
  local t=c.block(wx,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 b={right=true}
 local feet=c.y+32
 local obstacle=solid(c.x+20,feet-8)or solid(c.x+20,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do
  if solid(c.x+12,y)then support=true;break end
 end
 local enemy=c.enemy()
 local danger=enemy and enemy.dx>0 and enemy.dx<24 and math.abs(enemy.y-c.y)<32
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>18)then b.a=true
 elseif not c.grounded then b.a=c.lastA end
 if enemy and enemy.dx>0 and enemy.dx<48 and math.abs(enemy.y-c.y)<32 and c.grounded then b.b=c.poll%24<2 end
 return b
end
