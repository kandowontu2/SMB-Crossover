-- Ordinary-controller retiming of Bass's own route hooks for the camera fix.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_water_late.lua'))
local offAge,pipeAge=0,-1
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 local b=prior(c)
 if c.char==9 and c.areaType~=0 then
  local function pipe(t)return t==0x10 or t==0x11 or t==0x14 or t==0x15 end
  local wall=pipe(c.block(c.x+16,c.y+8))or pipe(c.block(c.x+16,c.y+24))
  if pipeAge>=0 and c.grounded and pipeAge>8 then pipeAge=-1 end
  if pipeAge<0 and c.grounded and wall then
   if offAge<5 then return{}end
   pipeAge=0
  end
  if pipeAge>=0 then
   -- A floor enemy behind a solid pipe is not a clear buster target. Give
   -- both real jumps a five-poll release and clear the pipe before aiming.
   b={right=true,a=pipeAge<20 or(pipeAge>=25 and pipeAge<56)}
   pipeAge=pipeAge+1
  end
 end
 if b.a and not c.lastA and offAge<5 then b.a=false end
 return b
end
