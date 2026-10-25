-- Controller discovery only. No game state writes; a fixed replay is required.
return function(c)
 local b={a=c.poll%6<3,b=c.poll%24<2}
 if c.world~=0 or c.level~=0 then b.right=true;return b end
 local target=48
 b.up=c.y>target+2;b.down=c.y<target-2
 -- Rise before advancing into the first low question block. Native camera
 -- motion continues while the player deliberately holds horizontal position.
 b.right=c.y<74 and(c.x-c.camera<112 or c.r('ScrollLock')~=0)
 return b
end
