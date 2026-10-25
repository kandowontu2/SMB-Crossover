-- Natural Hard-mode mushroom and first upgrade, then a bounded weapon demo.
-- Wait changes only ordinary idle frames before firing at the real block.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local pickup=assert(dofile(root..'/tools/playthroughs/bill_easy_progression_t.lua'))
local remaining=SHOWCASE_WAIT or 0
local got,age,item=false,0,0
local log=assert(io.open(ROSTER_CONFIG.out..'hard-upgrade.csv','w'));log:write('poll,event,item,owned,selected,x,y\n')
local function owned(c)return c.r('InvOwnedLo',3)+256*c.r('InvOwnedHi',3)end
local function note(c,event)log:write(table.concat({c.poll,event,item,owned(c),c.r('InvSelected',3),c.x,c.y},',')..'\n');log:flush()end
return function(c)
 assert(c.r('CrossoverBehaviorVersion')==1,'This policy uses real Hard rules')
 local bits=owned(c)
 if not got and(bits&0xfffe)~=0 then
  got=true;age=0
  for n=1,6 do if(bits&(1<<n))~=0 then item=n end end
  note(c,'naturally-collected')
 end
 if got then
  age=age+1
  if age==1 then note(c,'demo')end
  if age>300 then return{}end
  -- Laser and Machine respond to held fire; the other weapons show fresh
  -- bursts, including the faster normal bullets after Rapid.
  local selected=c.r('InvSelected',3)
  local b=(selected==2 or selected==4)and age%90<78 or age%12<5
  return {b=b}
 end
 if c.status>0 and c.x>=1230 and c.x<=1256 and c.grounded and remaining>0 then
  if remaining==(SHOWCASE_WAIT or 0)then note(c,'ordinary-wait')end
  remaining=remaining-1;return{}
 end
 return pickup(c)
end
