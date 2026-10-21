-- Generic route-discovery starting policy. This is not a verified route.
-- Return function(context); the harness owns menu input, logging and replay.
-- Each agent may copy this file into its own uniquely named character policy.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
return function(c)
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.area
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0 end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 local small=(c.char==0 or c.char==8)and c.status==0
 local height=small and 16 or 32
 local feet=c.y+height
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local solid=function(wx,y)local t=c.block(wx,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if c.areaType==0 then
  -- Swim around mid-height and hold Right into the underwater exit pipe.
  if c.char==0 or c.char==8 then b.a=c.y>100 and not c.lastA
  else b.a=c.grounded and not c.lastA end
  b.b=c.poll%8==0
  if solid(c.x+20,c.y+8)then b.a=not c.lastA end
  return b
 end
 local e=c.enemy()
 b.b=(c.char==0 or c.char==8)or c.poll%8==0
 local obstacle=solid(c.x+24,c.y+height-8)or solid(c.x+24,c.y+8)
 local supportAhead=false
 local lookahead=c.char==3 and c.world==0 and c.level==0 and 40 or 20
 supportAhead=solid(c.x+lookahead,math.min(feet+8,232))
 local gap=not supportAhead
 local enemy=e and e.dx>0 and e.dx<45 and math.abs(e.y-c.y)<48
 if c.grounded and not c.lastA and(obstacle or gap or enemy or still>20)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<30 end
 -- Underground exit: walking into its vertical pipe enters normally.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2800 then b.a=false end
 return b
end
