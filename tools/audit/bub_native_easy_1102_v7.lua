-- Natural Easy encounter. The original actor jumps; native contact must stomp.
BUB_NATIVE_OBSERVER_CONFIG.output=OUTPUT
local easy_part,easy_step,easy_last='approach',0,0
local easy_lives,easy_base,easy_slot=nil,nil,nil
local easy_events,easy_min_y,easy_landed={},255,false
local function easy_x(i)
 if i then return ram(L.Enemy_X_Position+i)+256*ram(L.Enemy_PageLoc+i)end
 return r('Player_X_Position')+256*r('Player_PageLoc')
end
local function easy_event(kind)
 assert(#easy_events<16,'Bounded Easy event aggregate')
 local i=easy_slot or 0
 easy_events[#easy_events+1]={kind=kind,Main=BUB_OBSERVER.summary().completed_Main,x=easy_x(),y=r('Player_Y_Position'),
  enemy_slot=i,enemy_x=easy_x(i),enemy_y=ram(L.Enemy_Y_Position+i),enemy_ID=ram(L.Enemy_ID+i),
  enemy_flag=ram(L.Enemy_Flag+i),enemy_state=ram(L.Enemy_State+i)}
end
local function easy_label()return phase=='easy'and easy_part or phase end
local function easy_keys()
 if easy_part=='approach'then return{'right'}end
 if easy_part=='jump'then return{'right','a'}end
 return{}
end
local function easy_write(ok,why,q)
 local f=assert(io.open(OUTPUT..'easy-stomp.json','w'))
 f:write(BUB_OBSERVER.json({passed=ok,why=why,controller_only=true,ROM_sha256=Q.ROM_sha256,
  events=easy_events,source=q,initial_lives=easy_lives,final_lives=r('NumberofLives'),minimum_y=easy_min_y,
  native_Easy_only=true,full_stage=false,helpers_added=false,installed=false})..'\n');f:close()
end
local function easy_fail(why)local q=BUB_OBSERVER.finish();easy_write(false,why,q);assert(false,why)end
local function easy_begin()
 assert(r('CrossoverBehaviorVersion')==0,'Actual native menu remains Easy')
 phase='easy';age=0;easy_lives=r('NumberofLives');easy_base=BUB_OBSERVER.summary();easy_last=easy_base.completed_Main
 easy_event('natural-approach');shot('easy-cold-spawn')
end
local function easy_tick(finish)
 if r('SelectedCharacter')~=39 or r('OperMode')~=1 or r('GameEngineSubroutine')~=8 or r('NumberofLives')~=easy_lives then easy_fail('Natural Easy encounter injured or lost owner/life')end
 local q=BUB_OBSERVER.summary();if q.completed_Main==easy_last then return end
 assert(q.completed_Main==easy_last+1,'Actual completed Easy Main cadence');easy_last=q.completed_Main;easy_step=easy_step+1
 easy_min_y=math.min(easy_min_y,r('Player_Y_Position'))
 if q.completed_Main-easy_base.completed_Main>650 then easy_fail('Bounded natural Easy encounter did not stomp/land')end
 if q.launches~=easy_base.launches or q.captures~=easy_base.captures then easy_fail('Native stomp encounter unexpectedly used a bubble')end
 if easy_part=='approach'then
  local best,gap=nil,10000
  for i=0,5 do
   local flag=ram(L.Enemy_Flag+i);local d=easy_x(i)-easy_x()
   if flag>0 and flag<128 and ram(L.Enemy_ID+i)==6 and ram(L.Enemy_State+i)&32==0 and d>0 and d<gap then best,gap=i,d end
  end
  if best and gap<=40 then
   assert(gap>=24,'Actual native enemy remains safely ahead at takeoff')
   easy_slot=best;easy_part='jump';easy_step=0;easy_event('original-jump-toward-native-Goomba')
  end
 elseif easy_part=='jump'then
  if q.native_enemy_stomps>easy_base.native_enemy_stomps then
   assert(q.native_bounce_entries>easy_base.native_bounce_entries,'Actual native stomp bounce entry')
   easy_part='bounce';easy_step=0;easy_event('native-EnemyStomped');shot('earned-native-stomp')
  elseif easy_step>=100 then easy_fail('Original controller jump did not earn actual native EnemyStomped')end
 elseif easy_part=='bounce'then
  if q.source_native_bounce_restarts>easy_base.source_native_bounce_restarts and easy_step>=2 then
   easy_event('native-impulse-original-D36B-restart');easy_part='land';easy_step=0
  elseif easy_step>=12 then easy_fail('Native stomp impulse did not restart original D36B')end
 elseif easy_part=='land'and easy_step>=40 and r('Player_State')==0 and r('Player_Y_Position')==176 then
  assert(q.source_total_jump_starts>=easy_base.source_total_jump_starts+2,'Original takeoff and genuine native-bounce restart both executed')
  easy_event('real-ground-support-after-bounce');local final=BUB_OBSERVER.finish();easy_write(final.passed,'native-Easy-stomp-original-bounce-landed',final)
  assert(final.passed,'Actual source/header/hardware Easy observer');shot('easy-supported-rest');finish()
 end
end
