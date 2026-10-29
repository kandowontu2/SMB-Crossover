-- Input-only discovery: long-neck Mario needs time to line up a Goomba stomp.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local jumpHold=0
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==2,'Actual SuperMaaa menu alternate')
 assert(c.r('MaaaLength')<=160,'Original maximum neck length')
 local b=route(c)
 local e=c.enemy()
 if c.world==0 and c.level==0 and e and e.id==6 and e.state<2
  and e.dx>0 and e.dx<80 and math.abs(e.y-c.y)<64 and c.grounded and not c.lastA then
  b.a=true;jumpHold=32
 end
 if jumpHold>0 then b.a=true;jumpHold=jumpHold-1 end
 return b
end
