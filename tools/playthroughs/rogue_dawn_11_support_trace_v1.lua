-- Finite read-only diagnostic successor. Keep the V2 controller unchanged.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v2.lua'))
print('SOURCE_SUPPORT poll,x,y,yHigh,action,gravity,vy,centerX,radiusX,centerY,radiusY,footY,left,center,right,leftAttr,centerAttr,rightAttr,a,b,leftPad,rightPad')
local count=0
return function(c)
 local b=route(c)
 if c.x>=320 and c.x<=350 and count<160 then
  local x=c.r('RdX')+256*c.r('RdRoomHi')
  local y=c.r('RdY')
  local rx,ry=c.r('RdRadiusX'),c.r('RdRadiusY')
  local fy=y+ry+1
  local l,m,r=c.block(x-rx,fy),c.block(x,fy),c.block(x+rx,fy)
  local t=ROSTER_CONFIG.rogue_tile_attributes
  print('SOURCE_SUPPORT '..table.concat({c.poll,c.x,c.y,c.yHigh,c.r('RdAction'),c.r('RdGravity'),c.r('RdVY'),x,rx,y,ry,fy,l,m,r,t[l+1],t[m+1],t[r+1],b.a and 1 or 0,b.b and 1 or 0,b.left and 1 or 0,b.right and 1 or 0},','))
  count=count+1
 end
 return b
end
