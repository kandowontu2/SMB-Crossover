-- Reuse old stage-local controls only after a new complete stage entry. A
-- verified branch prefix ends midway through its current room; continue that
-- room with live ordinary navigation instead of restarting its old stream.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local reference=assert(dofile(root..'/tools/playthroughs/luigi34_after_tunnel_policy.lua'))
local localTail=assert(dofile(root..'/tools/playthroughs/native33_finish_policy.lua'))
local initialStage,initialized
return function(c)
 local key=c.world..'-'..c.level
 if not initialized then
  initialized=true
  if c.x>64 then initialStage=key end
 end
 if key==initialStage and key~='0-1'then return localTail(c)end
 return reference(c)
end
