-- Ordinary Pit traversal, real ground beneath1248, then clear-side row mount.
local function chooseStock(c)
 local a=stockObserve()
 if a then
  stock.phase='collect'
  if not stock.mount then
   local edge=C.target_x+16;local cells={}
   for _=1,8 do local tile=c.block(edge,C.target_y);cells[#cells+1]={x=edge,tile=tile};if tile==0 then break end;edge=edge+16 end
   local clear=edge+16;assert(clear<1376 and c.block(clear,208)~=0,'Actual supported right-side clearance before second pit')
   stock.mount={phase='clear',edge=edge,clear=clear,cells=cells,since=guestReturns,request=state()}
  end
  local q=stock.mount;assert(guestReturns-q.since<420,'One ordinary Pit Flower row mount')
  if q.phase=='clear'then
   if c.grounded and c.y>=160 and c.x>=q.clear and c.x<=q.clear+2 and not lastA then
    q.settle=(q.settle or 0)+1
    if q.settle>=8 then q.phase='rise';q.takeoff=guestReturns;q.stand=state();q.camera=c.camera;return{a=true}end
   else q.settle=0 end
   return{right=c.x<q.clear,left=c.x>q.clear+2}
  elseif q.phase=='rise'then
   if c.y<=C.target_y-32 then q.phase='onto';q.clearance=state()else return{a=guestReturns-q.takeoff<34}end
  end
  assert(q.phase=='onto');return{right=c.x<a.x-3,left=c.x>a.x+3,a=guestReturns-q.takeoff<34}
 end
 if stock.phase=='travel'and c.x<C.target_x-56 then return travel(c)end
 if stock.phase=='travel'then stock.phase='align';stock.phaseStart=guestReturns end
 if stock.phase=='align'then
  assert(guestReturns-stock.phaseStart<450,'One actual ground/camera head alignment')
  if not stock.row then
   local left=C.target_x;local cells={}
   for _=1,8 do local tile=c.block(left-16,C.target_y);cells[#cells+1]={x=left-16,tile=tile};if tile==0 then break end;left=left-16 end
   stock.row={left=left,clear=left-24,cells=cells,at=state(),camera=c.camera}
  end
  if not c.grounded or c.y<160 then
   stock.last_row_exit={state=state(),camera=c.camera,relativeX=c.x-c.camera}
   return{left=c.x>math.max(stock.row.clear,c.camera+1)}
  end
  stock.ground=stock.ground or{state=state(),camera=c.camera,relativeX=c.x-c.camera,feet={c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)}}
  local center=C.target_x-7
  if c.x>=center and c.x<=center+2 and not lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=16 then
   stock.phase='head';stock.headAt=guestReturns;stock.request=state();stock.authored_tile=c.block(C.target_x,C.target_y);return{a=true}
  end
  return{right=c.x<center,left=c.x>center+2}
 elseif stock.phase=='head'then
  assert(guestReturns-stock.headAt<160,'One real Flower head admission')
  if c.state==1 and c.vy>=128 then stock.admission=stock.admission or state()end
  return{a=guestReturns-stock.headAt<24}
 end
 error('Unknown Pit Flower phase '..stock.phase)
end
