-- Scrooge controller discovery. Read-only telemetry; ordinary buttons only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scrooge_route_bump_observe.lua'))
local previousX,still=nil,0
local exitLaunch
return function(c)
 local b=base(c)
 if c.char==12 and c.areaType==0 and c.x>=2854 then
  if c.x>=2935 and c.x<3000 and c.grounded and c.y>=160 and not c.lastA and (not exitLaunch or c.poll-exitLaunch>80) then
   exitLaunch=c.poll
  end
  return {right=true,b=c.poll%8<3,a=c.x<3000 and exitLaunch and c.poll-exitLaunch<4}
 end
 if c.char~=12 or c.areaType~=0 or c.x>=2960 then return b end
 if c.x==previousX then still=still+1 else still=0 end
 previousX=c.x
 local function solid(x,y)
  local t=c.block(x,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 local wall=solid(c.x+32,c.y+8) or solid(c.x+32,c.y+24)
 local gap=not solid(c.x+24,math.min(c.y+40,232))
 local pogo=c.r('ScPogo')~=0
 local enemy=false
 for slot=0,5 do
  local flag=c.r('Enemy_Flag',slot)
  if flag>0 and flag<128 and c.r('Enemy_ID',slot)<0x15 then
   local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
   local y=c.r('Enemy_Y_Position',slot)
   if x>c.x and x<c.x+72 and math.abs(y-c.y)<72 then enemy=true end
  end
 end
 return {right=true,b=not c.grounded or pogo or c.poll%8<3,down=not c.grounded or pogo,
         a=c.grounded and not pogo and not c.lastA and (wall or gap or enemy or still>16)}
end
