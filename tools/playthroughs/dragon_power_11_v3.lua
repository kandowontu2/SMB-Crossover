-- Controller-only successor. Source floor probes are anchor+2/+14; looking
--32px ahead triggers a too-early jump for the source1.25px walking speed.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
return function(c)
 assert(c.char==24,'Actual Goku menu identity')
 local b=route(c)
 if c.world==0 and c.level==0 then
  local e=c.enemy()
  local function solid(x,y)
   local t=c.block(x,y)
   return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
  end
  if c.grounded and not c.lastA and b.a then
   local feet=c.y+32
   local obstacle=solid(c.x+42,feet-8) or solid(c.x+42,c.y+8)
   local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
   if not obstacle and not danger then
    local support,farSupport=false,false
    for y=math.min(feet+8,232),232,16 do
     if solid(c.x+16,y) then support=true end
     if solid(c.x+32,y) then farSupport=true end
    end
    -- Keep intentional block/pickup jumps on solid ground intact.
    if not farSupport then b.a=not support end
   end
  end
  -- Preserve the original air-attack behavior; don't invoke it inadvertently.
  b.b=c.grounded and not b.a and e and e.dx>0 and e.dx<30 and math.abs(e.y-c.y)<40 or false
 end
 return b
end
