-- MM/Bass route tail. Only ordinary controller buttons; telemetry is read-only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/megaman_bass_policy.lua'))
local tail=assert(dofile(root..'/tools/playthroughs/megaman_bass_tail_nav.lua'))
local pillarLanded,stairsMounted=false,false
local holdA,cooldown=0,0
local exitPhase='back'
local highWait,highCleared=false,false
local function finish(b,c)
 if cooldown>0 then cooldown=cooldown-1 end
 if b.a and holdA==0 and cooldown==0 then holdA=32 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end end
 return b
end
return function(c)
 local b=base(c)
 if c.world>0 or(c.world==0 and(c.level>=3 or(c.level==2 and c.x>=800)))then return finish(tail(c),c)end
 local e=c.enemy()
 if c.world==0 and c.level==2 and not highCleared then
  if c.grounded and c.y==96 and c.x>=548 and c.x<640 then highWait=true end
  if highWait then
   holdA=0;cooldown=0
   if e and e.id==6 and math.abs(e.dx)<160 then
    if c.x<558 then return {right=true} end
    if c.x>562 then return {left=true} end
    local dir=e.dx>=0 and 1 or 2
    if c.r('PlayerFacingDir')~=dir then return {right=dir==1,left=dir==2} end
    return {b=c.poll%8<3}
   end
   highCleared=true
  end
 end
 if c.world==0 and c.level==2 and c.x>=600 and c.x<656 and c.y>=64 then
  b.right=true;b.left=false
  if c.grounded and c.x>=614 and not c.lastA then b.a=true end
  return finish(b,c)
 end
 if c.world==0 and c.level==1 and c.areaType==2 then
  if c.x>=2580 then
   holdA=0;cooldown=0
   if exitPhase=='back' then
    local target=math.max(2616,c.camera+1)
    if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter' end
    return {right=c.x<target,left=c.x>target+3}
   end
   return {right=true}
  end
  if not stairsMounted and c.x>=2144 and c.x<2208 then
   if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return {right=true,b=true} end
   return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA,b=c.poll%8<3},c)
  end
  if c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then
   holdA=0;cooldown=0;return {right=true,b=c.poll%8<3}
  end
  if not pillarLanded and c.x>=1944 and c.x<1984 then
   if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c) end
   return finish({right=c.x<1960,left=c.x>1964},c)
  end
 end
 return finish(b,c)
end
