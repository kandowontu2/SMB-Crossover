-- Input-only top-stair landing; keep the qualified airborne Arrow/gap route.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_darkwing_air_arrow_v7.lua')
local phase='approach';local which=1
local stairs={{begin=2080,peak=2192,edge=2208,far=2240,finish=2304},{begin=2336,peak=2432,edge=2448,far=2480,finish=2544}}
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
local function change(c,p)
 if phase~=p then phase=p;print('Darkwing stairs '..which..' '..p..' x'..c.x..' y'..c.y..' previous'..c.r('DwPrevious'))end
end
return function(c)
 if c.world~=0 or c.level~=0 then return base(c)end
 assert(c.char==12 and c.r('DarkwingVariant')==1,'Actual Darkwing stair owner')
 local s=stairs[which]
 if s and c.x>=s.finish then which=which+1;phase='approach';s=stairs[which]end
 if s and c.x>=s.begin and c.x<s.finish then
  -- Bind the genuine native61 top and the separated next platform. Never
  -- infer a stair from an arbitrary overhead cell or bypass missing terrain.
  local nativeTop=c.block(s.peak+8,145)==0x61 and c.block(s.far+8,145)==0x61
   and not solid(c.block(s.edge+8,145))
  if nativeTop then
   if phase=='approach'then change(c,'climb')end
   local prev=c.r('DwPrevious')
   if phase=='climb-air'and c.grounded then change(c,'climb')end
   if(phase=='climb'or phase=='climb-air')and c.x>=s.peak and c.y+32<=144 then change(c,'land')end
   if phase=='land'then
    local b={right=c.x<s.peak+2,left=c.x>s.peak+6}
    if c.grounded and c.y+32<=144 and(prev&128)==0 then change(c,'cross');return{right=true,a=true}end
    return b
   end
   if phase=='cross'then
    if c.grounded and c.x>=s.far-8 then change(c,'walkout')end
    return{right=true,a=true}
   end
   if phase=='walkout'then return{right=true}end
   if phase=='climb-air'then return{right=true,a=true}end
   local wall=solid(c.block(c.x+24,c.y+8))or solid(c.block(c.x+24,c.y+24))
   if c.grounded and wall and(prev&128)==0 then change(c,'climb-air');return{right=true,a=true}end
   return{right=true}
  end
 end
 -- A head-height cell alone is not a wall. Suppress the legacy Arrow
 -- admission before it can mutate its private phase; let native Right walk
 -- below a clear forward body corridor. The two real pipe faces stay solid.
 if c.x>450 and c.grounded and c.vx==0 then
  local head=solid(c.block(c.x+16,c.y-20))or solid(c.block(c.x+32,c.y-20))
  local body=false
  for _,dx in ipairs({16,32})do for _,dy in ipairs({8,24})do if solid(c.block(c.x+dx,c.y+dy))then body=true end end end
  if head and not body then return{right=true}end
 end
 return base(c)
end
