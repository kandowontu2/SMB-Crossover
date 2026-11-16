-- Mature native Star feedback. Every action remains an ordinary controller input.
local function signedByte(v)return v<128 and v or v-256 end
local function originalGroundStop(s)
 local v,tick,f,x=s.speed,ram2(0x3f),ram2(0x394),s.x
 local dir=ram2(0x804)==2 and -1 or 1
 for _=1,256 do
  if v==0 then return x end
  tick=(tick+1)&255;if tick&3==0 then v=math.max(0,v-56)end
  f=f+(v&255);local dx=(v>>8)+(f>=256 and 1 or 0);f=f&255;x=x+dir*dx
 end
 error('Original actual coast bound')
end
local function originalMatchTicks(s,actorSpeed)
 local v,tick,n=s.speed,ram2(0x3f),0;local target=math.min(832,math.abs(actorSpeed)*16)
 while v<target do n=n+1;assert(n<=64,'Original native actor speed match bound');tick=(tick+1)&255;if tick&3==0 then v=math.min(832,v+63)end end
 return n
end
local function bounceIntercept(s,a)
 a.vx=signedByte(r('Enemy_X_Speed',a.slot));a.vy=signedByte(r('Enemy_Y_Speed',a.slot));a.direction=r('Enemy_MovingDir',a.slot)
 stock.intercept=stock.intercept or{request=state(),actor=a,since=mainReturns}
 assert(mainReturns-stock.intercept.since<750,'One bounded ordinary native Star bounce intercept')
 local q=stock.bounce
 if not q then
  q={samples={},turns={},first=state(),actor=a,since=movementReturns};stock.bounce=q
  q.terrain={}
  for x=1600,1760,16 do q.terrain[#q.terrain+1]={x=x,head=block(x,144),body=block(x,184),floor=block(x,208)}end
 end
 local changed=q.vx~=a.vx or(q.vy or 0)<=0 and a.vy>0
 if changed and#q.turns<8 then q.turns[#q.turns+1]={state=state(),actor=a}end
 if changed or not q.lastSample or movementReturns-q.lastSample>=16 then
  q.samples[#q.samples+1]={state=state(),actor=a,buttons=buttons};if#q.samples>16 then table.remove(q.samples,9)end;q.lastSample=movementReturns
 end
 q.vx=a.vx;q.vy=a.vy
 if q.jump then
  local n=movementReturns-q.jump;q.minimum_y=math.min(q.minimum_y,s.y)
  buttons=n<8 and(q.dir+64+8+128)or n<36 and 8 or 0
  if n>=36 and s.native==0 and s.air==0 then q.jump=nil end
  return
 end
 if q.prelean then
  buttons=q.dir+64+8
  if movementReturns-q.prelean>=4 then
   q.prelean=nil;q.jump=movementReturns;q.takeoff={state=state(),actor=a};q.minimum_y=s.y;buttons=q.dir+64+8+128
  end
  return
 end
 -- The original motor owns crash/recovery and air movement. Do not manufacture
 -- speed while those gates are active or steer from a stale standing snapshot.
 if s.native~=0 or s.air~=0 or s.crash~=0 or s.recovery~=0 or s.heat~=0 then return end
 assert(ram2(0x52)==0 and ram3(0xa905)==56 and ram3(0xa901)==63,'Actual original flat coast/acceleration')
 local lead=originalMatchTicks(s,a.vx);local goal=a.x+(a.vx/16)*lead-8
 local stop=originalGroundStop(s);q.last_feedback={state=state(),actor=a,lead=lead,goal=goal,projected_stop=stop}
 -- A coming Star is allowed to approach. Chase in its actual direction rather
 -- than charging back underneath it, or parking at the old source-only X.
 if a.vx>0 and stop<goal-3 then buttons=65
 elseif a.vx<0 and stop>goal+3 then buttons=66 end
 local gap=a.x-s.x;local dir=ram2(0x804)
 if s.speed>=630 and a.y<s.y-12 and math.abs(gap)<48 and(dir==1 and gap>=0 or dir==2 and gap<=0)then
  q.prelean=movementReturns;q.dir=dir;q.prelean_request={state=state(),actor=a};buttons=dir+64+8
 end
end
