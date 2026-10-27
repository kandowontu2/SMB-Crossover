-- Natural Bass1-1 controller correction. No state writes or injected actors.
-- Solid terrain takes priority over the tracked stop-and-shoot branch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_bass_v34_policy.lua'))
local offAge=0
local headPhase,headAge,headJump,headSeen='approach',0,0,false
local pipePhase,pipeAge,pipeTarget,pipeY,pipeSecond='none',0,0,0,false
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
return function(c)
 offAge=c.lastA and 0 or offAge+1
 local b=prior(c)
 if c.char~=9 or c.world~=0 or c.level~=0 then return b end
 -- Settle below the actual first block, release A, then jump at X332.
 -- Displacement/reveal/rise/pickup remain native; inputs alone prove none.
 if headPhase~='done' and c.x>=280 then
  headAge=headAge+1
  local item
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
    item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
   end
  end
  if item then headSeen=true;headPhase='collect'end
  if c.status>0 or(headSeen and not item)or headAge>180 or c.x>430 then
   headPhase='done';print('BASS11 head window ended; power='..c.status..' seenItem='..tostring(headSeen))
  elseif headPhase=='collect'then
   if item.x<c.camera+4 then headPhase='done'
   else
    local out={right=c.x<item.x-3,left=c.x>item.x+10}
    if item.state>=128 and item.y<c.y-8 and c.grounded and offAge>=5 then headJump=18 end
    if headJump>0 then out.a=true;headJump=headJump-1 end
    return out
   end
  elseif headPhase=='approach'then
   if c.grounded and c.x>=330 and c.x<=334 and c.y>=160 and offAge>=5 then
    headPhase='jump';headJump=18;print('BASS11 physical head jump x='..c.x)
   else return{right=c.x<330,left=c.x>334}end
  end
  if headPhase=='jump'then
   if headJump>0 then headJump=headJump-1;return{a=true,b=c.poll%24<12}end
   if c.grounded then headPhase='approach'end
   return{}
  end
 end
 local wall=solid(c,c.x+24,c.y+8)or solid(c,c.x+24,c.y+24)
 if pipePhase=='none' and c.grounded and wall then
  pipePhase='release';pipeAge=0;pipeY=c.y;pipeSecond=false
  pipeTarget=math.floor((c.x+24)/16)*16
  for _=1,6 do
   if not solid(c,pipeTarget,pipeY+8)and not solid(c,pipeTarget,pipeY+24)then break end
   pipeTarget=pipeTarget+16
  end
  pipeTarget=pipeTarget+8
 end
 if pipePhase=='release'then
  if offAge>=5 then pipePhase='jump';pipeAge=0 end
  return{right=true,a=pipePhase=='jump'}
 elseif pipePhase=='jump'then
  pipeAge=pipeAge+1
  if c.grounded and pipeAge>8 then
   if c.x>=pipeTarget then pipePhase='none';return b end
   pipePhase='release';return{right=true}
  end
  if pipeAge>90 then pipePhase='none';return b end
  -- Native Bass air jump accepts a fresh A only with XgJumpUsed zero.
  -- Five release polls precede the second press; no velocity/result is seeded.
  if pipeAge==24 then pipeSecond=c.r('XgJumpUsed')==0 and c.x<pipeTarget and c.y>48 end
  return{right=true,a=pipeAge<18 or(pipeSecond and pipeAge>=24 and pipeAge<43)}
 end
 return b
end
