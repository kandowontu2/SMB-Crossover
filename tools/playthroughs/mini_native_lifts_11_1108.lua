-- Appended to the ordinary Mini 1-1 controller replay. This policy observes
-- the real platform and produces pad inputs. It never creates a platform.
local mini_lift_left = {[608]=560,[736]=688,[912]=864}
local mini_lift_runs = {}
local function mini_lift_inputs(s, obstacle, x)
 local left = obstacle and mini_lift_left[obstacle.left]
 if not left then return end
 local row = mini_lift_runs[left]
 if not row then
  row = {left=left,center=left+16,initial_top=192,width=32,stage='1-1',pipe=obstacle.left}
  mini_lift_runs[left] = row
  phases.fullstage.lifts = phases.fullstage.lifts or {}
  phases.fullstage.lifts[#phases.fullstage.lifts+1] = row
 end
 if row.departed then return end
 local slot = ram(0xc30b)-1
 local target = slot>=0 and slot<6 and read(L.Enemy_Flag+slot)==1 and read(L.Enemy_ID+slot)==0x25
  and read(L.Enemy_X_Position+slot)+256*read(L.Enemy_PageLoc+slot)==left
 local floor = supported(s)
 if target then
  local top = read(L.Enemy_Y_Position+slot)
  if not row.spawn_top then row.spawn_top=top;row.spawn_frame=frame;row.slot=slot end
  if ram(0xc30d)==slot+1 then
   if not row.boarded then
    row.boarded=true;row.board_frame=frame;row.board_top=top;row.board_x=x
   end
   row.minimum_top=math.min(row.minimum_top or top,top)
   if row.departure_press and s.queued==12 then return {right=true,b=true,a=true} end
   -- Release A and build a little speed on the platform before taking off.
   if floor and top<=obstacle.top+10 then
    if x<left+19 then return {right=true,b=true} end
    if s.held&128==0 then
     row.departure_press=true
     return {right=true,b=true,a=true}
    end
   end
   return {}
  end
  if row.departure_press then
   if s.queued==12 or s.current==12 or s.current==13 or s.vy<0 then
    row.departed=true;row.departure_frame=frame;row.departure_x=x;row.departure_top=top
    return {right=true,b=true,a=true}
   end
  end
  if x>=left-23 and x<=left+26 then
   if floor then
    if top>=166 and s.held&128==0 then return {right=true,b=true,a=true} end
    if top<166 then return {} end
    return {right=true,b=true}
   end
   return {right=x<left+5,b=true,a=true}
  end
 end
 if x>=left-12 and x<=left+29 and not row.boarded then return {} end
end
