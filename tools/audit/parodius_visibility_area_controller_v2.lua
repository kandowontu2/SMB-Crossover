-- Ordinary buttons only. Target positions come from current native metatiles.
-- No result, position, inventory, RNG, queue, or actor state is written.
PARODIUS_AREA_CONTROLLER_FACTORY=function(event)
 local target,lastPhase=nil,nil
 local passed={}
 local function center(c,b)
  local screen=c.x-c.camera
  if screen<111 then b.right=true elseif screen>113 then b.left=true end
 end
 local function vertical(c,b,y)
  if c.y<y then b.down=true elseif c.y>y then b.up=true end
 end
 local function phase(name,c)
  if name~=lastPhase then lastPhase=name;event('area-controller-phase',{phase=name,player_x=c.x,player_y=c.y,camera=c.camera,target=target})end
 end
 return function(c,initialArea,currentArea)
  if c.engine~=8 then return{}end
  local b={a=c.poll%8<2}
  if initialArea and currentArea and currentArea~=initialArea then
   phase('new-area-safe-control',c);center(c,b);vertical(c,b,100);return b
  end
  if target and c.x>target.entry_high then
   passed[target.key]=true;event('natural-pipe-target-passed',{target=target,player_x=c.x,player_y=c.y,camera=c.camera});target=nil
  end
  if not target then
   local first=(c.camera//16)*16
   for wx=first,first+224,16 do
    for yy=64,192,16 do
     local key=wx..':'..yy
     if not passed[key]and c.block(wx,yy)==0x10 and c.block(wx+16,yy)==0x11 then
      -- Compiled VvMovement/HandlePipeEntry contact: playerX=left+5..10,
      -- playerY=top-8..top+7. Stay one pixel above until centered.
      local q={key=key,left=wx,top=yy,entry_low=wx+5,entry_high=wx+10,pre_y=yy-9}
      if c.x<=q.entry_high then
       target=q;event('natural-enterable-pipe-found',{x=wx,top=yy,entry_low=q.entry_low,entry_high=q.entry_high,pre_y=q.pre_y,player_x=c.x,player_y=c.y,camera=c.camera});break
      else passed[key]=true;event('natural-pipe-already-passed',{target=q,player_x=c.x,player_y=c.y,camera=c.camera})end
     end
    end
    if target then break end
   end
  end
  if not target then phase('discover-ahead',c);center(c,b);vertical(c,b,104);return b end
  if c.y~=target.pre_y then
   phase('align-above-pipe',c);vertical(c,b,target.pre_y)
   -- Left plus native autoscroll slows world advance near a target; it
   -- cannot be assumed to move backwards at native speed tier0.
   if c.x>=target.entry_low-16 then b.left=true else center(c,b)end
  elseif c.x<target.entry_low then
   phase('approach-aligned',c);center(c,b)
  else
   phase('native-down-entry',c);b.left=true;b.down=true
  end
  assert(not(b.left and b.right)and not(b.up and b.down),'Exclusive ordinary area controller directions')
  return b
 end
end
