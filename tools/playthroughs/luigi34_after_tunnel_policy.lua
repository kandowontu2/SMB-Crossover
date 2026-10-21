-- Ordinary controller discovery after the current underground crowd branch.
-- The prefix already ends inside1-2, so do not restart a stage-local stream
-- for that partial room. Subsequent stages may reuse genuine old inputs.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local reference=assert(dofile(root..'/tools/playthroughs/native33_stage_reference.lua'))
local localTail=assert(dofile(root..'/tools/playthroughs/native33_finish_policy.lua'))
local pipes=assert(dofile(root..'/tools/playthroughs/luigi34_pipe_controls.lua'))
return function(c)
 if c.world==0 and c.level==1 then
  -- The verified exit branch settles at2617/Y128. Keep the controls neutral
  -- vertically so the generic wall-jump heuristic does not jump over the
  -- horizontal pipe mouth while trying to move through its side entrance.
  if c.areaType==2 and c.x>=2580 then return{right=true,b=true}end
  local b=pipes(c);if b then return b end
  return localTail(c)
 end
 return reference(c)
end
