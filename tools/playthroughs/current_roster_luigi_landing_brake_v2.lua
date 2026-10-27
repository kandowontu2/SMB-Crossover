-- Controller-only successor to the observed ground-side contact at1250.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local function corridor(c,e)
 local first,last=c.x+2,e.x+14
 if last<first or last-first>144 then return false end
 local function clear(x)
  for y=112,200,8 do if c.block(x,y)~=0 then return false end end
  local t=c.block(x,216)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 for x=first,last,8 do if not clear(x)then return false end end
 return clear(last)
end
return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='luigi'or ROSTER_CONFIG.mode_value~=0 or c.char~=8
  or c.r('MarioVariant')~=1 or c.world~=0 or c.level~=0 or c.areaType~=1
  or c.yHigh~=1 or c.grounded or c.vy==0 or c.vy>=128 then return b end
 local e=c.enemy()
 if not e or e.id~=6 or e.state>=2 or e.y~=184 or e.dx<=20 or e.dx>=100
  or c.y<e.y-80 or c.y+32>=e.y+14 then return b end
 local i=e.slot
 if not i or i%1~=0 or i<0 or i>=6 then return b end
 local flag=c.r('Enemy_Flag',i)
 if flag==0 or flag>=128 or c.r('Enemy_ID',i)~=6 or c.r('Enemy_State',i)>=2
  or c.r('Enemy_Y_HighPos',i)~=1 or c.r('Enemy_Y_Position',i)~=184
  or c.r('Enemy_BoundBoxCtrl',i)~=9
  or c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)~=e.x
  or e.x-c.x~=e.dx or not corridor(c,e)then return b end
 -- Release running/A and brake before the floor resets downward velocity.
 -- The unchanged base owns the next ordinary ground jump and all other travel.
 b.b=false;b.right=false;b.left=true;b.a=false
 return b
end
