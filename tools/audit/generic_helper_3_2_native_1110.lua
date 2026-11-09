-- Controller-only Easy Scrooge 3-2. Observe only actual native slots and camera.
local C=assert(witness)
local function r(name,i)
 return emu.read(assert(C.symbols[name],name)+(i or 0),emu.memType.nesDebug)
end
local function pos(low,high,i) return r(low,i)+256*r(high,i) end
local function area() return 32*r('AreaType')+r('AreaAddrsLOffset') end
local function camera()
 return pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),pos('ScreenRight_X_Pos','ScreenRight_PageLoc')
end
local function playerX() return pos('Player_X_Position','Player_PageLoc') end
local function active(engine)
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==engine
end
local function stage()
 return r('WorldNumber')==2 and r('LevelNumber')==1 and area()==0x35
end
local function identity()
 return r('SelectedCharacter')==12 and r('DarkwingVariant')==0 and r('CrossoverBehaviorVersion')==0
    and r('CheatInvincible')==0 and r('CheatStartLevel')==0x29
end
local function json(v)
 if type(v)=='string' then return '"'..v:gsub('[%z\1-\31\\"]',function(c)
  return ({['"']='\\"',['\\']='\\\\'})[c] or string.format('\\u%04x',c:byte()) end)..'"' end
 if type(v)~='table' then return tostring(v) end
 local rows={}
 if #v>0 then
  for i,a in ipairs(v) do rows[i]=json(a) end
  return '['..table.concat(rows,',')..']'
 end
 local keys={};for k in pairs(v) do keys[#keys+1]=k end;table.sort(keys)
 for i,k in ipairs(keys) do rows[i]=json(k)..':'..json(v[k]) end
 return '{'..table.concat(rows,',')..'}'
end

local frame,poll,menuWait,age=0,0,0,0
local phase,buttons,lastA='menu',{},false
local firstLives,lastLives,losses,deathSeen=nil,nil,0,false
local firstActive,maxX,maxCamera,lastAdvance=nil,0,0,0
local screenshots,menuEvents,progress={}, {}, {}
local function shot(name)
 if screenshots[name] then return end
 local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 screenshots[name]=frame
end
local function state()
 local left,right=camera()
 return {frame=frame,poll=poll,x=playerX(),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),
         player_state=r('Player_State'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),
         mode=r('OperMode'),task=r('OperMode_Task'),camera_left=left,camera_right=right,
         world=r('WorldNumber')+1,level=r('LevelNumber')+1,area=area(),area_pointer=r('AreaPointer')}
end
local function actor(i)
 return {r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),
         pos('Enemy_X_Position','Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i)}
end
local function owns(i)
 local owner=r('HpActorOwner',i)
 return owner>=1 and owner<=3 and r('HpRecord',owner-1)==10
end
local function context()
 return phase=='play' and stage() and identity() and (active(8) or active(10))
end
local function hook(name,callback)
 local h=C.hooks[name]
 emu.addMemoryCallback(function()
  if not context() then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom
     or mapped.address~=h.bank*8192+(h.pc&8191) then return end
  for i,v in ipairs(h.bytes) do
   assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact mapped hook bytes '..name)
  end
  callback()
 end,emu.callbackType.exec,h.pc)
end

local birth,visible,firstCarry,lastCarry,departure,searchLast,scanFirst,scanLast
local births,carries,movingCarries,searches,fullSearches,maxOccupied,eligibleScans=0,0,0,0,0,0,0
local lossBeforeVisible,badCamera,windowStarted,windowExited=false,false,false,false
local scanRows,seenLeft,searchLeft={}, {}, {}
local previousScan,dropped=0,0
local function snapshot()
 local left,right=camera()
 local row={frame=frame,camera_left=left,camera_right=right,occupied=0,slots={},timer=r('TimerControl')}
 for i=0,5 do
  local a=actor(i)
  row.slots[i+1]=a
  if a[1]~=0 then row.occupied=row.occupied+1 end
 end
 if right-left~=255 then badCamera=true end
 return row
end
local function logWindow(row)
 -- Keep the bounded detail and the final sample even if prolonged activity fills it.
 local sig=json({row.camera_left,row.timer,row.slots,row.actual_free_search or false})
 if previousScan==sig then return end
 previousScan=sig
 if #scanRows<160 then scanRows[#scanRows+1]=row else dropped=dropped+1 end
end
hook('scan',function()
 local left=camera()
 if left<2983 or left>3018 then return end
 local row=snapshot()
 if not scanFirst then scanFirst=row end
 scanLast=row
 if left>=2985 and left<=3016 then
  windowStarted=true;eligibleScans=eligibleScans+1;seenLeft[left]=true
 end
 logWindow(row)
end)
hook('free',function()
 local h=r('HpSlot')
 if h>2 or r('HpRecord',h)~=10 then return end
 local left=camera()
 if C.released~=1 then
  assert(left>=2985 and left<=3016,'Allocator must enter only the authored Easy window')
 end
 searchLast=snapshot()
 if left<2985 or left>3016 then return end
 searches=searches+1;searchLeft[left]=true
 maxOccupied=math.max(maxOccupied,searchLast.occupied)
 if searchLast.occupied==6 then fullSearches=fullSearches+1 end
 searchLast.actual_free_search=true
 logWindow(searchLast)
end)
hook('construct',function()
 local i=emu.getState()['cpu.x']
 if i<0 or i>5 or not owns(i) then return end
 births=births+1
 if birth then return end
 local a=actor(i)
 local left,right=camera()
 local highest=nil
 if searchLast and searchLast.frame==frame and searchLast.camera_left==left then
  for j=5,0,-1 do if searchLast.slots[j+1][1]==0 then highest=j;break end end
 end
 birth={frame=frame,slot=i,flag=a[1],id=a[2],x=a[4],y=a[5],y_high=a[6],
        camera_left=left,camera_right=right,player_x=playerX(),prior_slot=highest,
        slots_before_constructor=searchLast}
end)
hook('carry',function()
 local i=emu.getState()['cpu.x']
 if i<0 or i>5 or not owns(i) or r('Enemy_Flag',i)~=1 or r('Enemy_ID',i)~=0x28
    or r('Enemy_State',i)~=0x60 or r('PlatformCollisionFlag',i)>=128 then return end
 local delta=r('R0');if delta>=128 then delta=delta-256 end
 local a=actor(i)
 local s={frame=frame,slot=i,player_x=playerX(),player_y=r('Player_Y_Position'),
          helper_x=a[4],helper_y=a[5],x_delta=delta,collision_flag=r('PlatformCollisionFlag',i)}
 carries=carries+1
 if delta~=0 then movingCarries=movingCarries+1 end
 if not firstCarry then firstCarry=s end
 lastCarry=s
end)

ROSTER_CONFIG={out=C.root..'/build/'}
local choose=assert(dofile(C.policy))
local function controlContext()
 local c={char=12,variant=0,poll=poll,r=r,frame=frame,stageFrame=age,x=playerX(),
          y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),
          vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),world=r('WorldNumber'),
          level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),
          camera=camera(),lastA=lastA,grounded=r('Player_State')==0}
 c.block=function(x,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
 end
 c.enemy=function()
  local nearest
  for i=0,5 do
   local flag,id,st=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
   if flag>0 and flag<128 and (id<0x15 or id==0x2d or id==0x33) and st<0x20 and not (id==6 and st>=2) then
    local x=pos('Enemy_X_Position','Enemy_PageLoc',i)
    local dx=x-c.x
    if dx>-160 and dx<160 and (not nearest or math.abs(dx)<math.abs(nearest.dx)) then
     nearest={slot=i,id=id,x=x,y=r('Enemy_Y_Position',i),state=st,dx=dx}
    end
   end
  end
  return nearest
 end
 return c
end
local boarding
local function travel()
 local c=controlContext()
 if firstCarry and frame-firstCarry.frame<12 then return {} end
 if visible and not firstCarry and owns(visible.slot) then
  local a=actor(visible.slot)
  local target=a[4]+8
  -- One ordinary A jump from the upper stair toward the actual moving deck.
  if not boarding and c.grounded and not c.lastA and c.y<=96 and target-c.x>=20 and target-c.x<=70 then
   boarding={frame=frame,poll=poll,x=c.x,y=c.y,deck_x=a[4],deck_y=a[5]}
  end
  if boarding and poll-boarding.poll<84 then
   return {right=c.x<target-11,left=c.x>target-5,a=poll-boarding.poll<26}
  end
 end
 return choose(c)
end
emu.addEventCallback(function()
 local pad=buttons
 if phase=='play' and stage() and active(8) then
  poll=poll+1;pad=travel();lastA=not not pad.a
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)

local function wait(n) coroutine.yield(n) end
local function press(key)
 buttons={[key]=true};wait(2);buttons={};wait(8)
end
local function ready(fn,max,tag)
 local start=frame
 while not fn() and frame-start<max do wait(1) end
 assert(fn(),'Real frontend handoff '..tag)
end
local function menuEvent(name)
 menuEvents[#menuEvents+1]={name=name,frame=frame,menu=r('CrossoverMenuState'),
      slot=r('CrossoverMenuIndex'),focus=r('CrossoverOptionsFocus'),start_level=r('CheatStartLevel'),
      other_cheats=r('CheatInvincible'),owner=r('SelectedCharacter'),alternate=r('DarkwingVariant'),
      difficulty=r('CrossoverBehaviorVersion')}
end
local menu=coroutine.create(function()
 wait(70);press('down');press('start')
 assert(r('CrossoverMenuState')==4,'Real title opens Options')
 press('down');press('down');press('a')
 assert(r('CrossoverMenuState')==6 and r('CrossoverOptionsFocus')==0,'Real Options opens Cheats')
 press('down')
 for i=1,9 do
  press('right');assert(r('CheatStartLevel')&31==i and r('CheatInvincible')==0,'Only Start Level changes')
 end
 assert(r('CheatStartLevel')==0x29,'Real Start Level selects 3-2')
 menuEvent('start-level-3-2');shot('start-level')
 press('b');press('b')
 ready(function() return r('CrossoverMenuState')==0 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,180,'title')
 press('start')
 ready(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,120,'roster')
 assert(r('CrossoverMenuIndex')==0,'Fresh roster starts at Mario')
 press('down')
 assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Scrooge Easy roster identity')
 menuEvent('scrooge-easy')
 press('start');phase='handoff';age=0
end)

local function keys(set)
 local a={};for k in pairs(set) do a[#a+1]=k end;table.sort(a);return a
end
local function finish(reason)
 local b,v=birth,visible
 local entered=not not (b and v and births==1 and not lossBeforeVisible and not badCamera
   and b.prior_slot==b.slot and b.flag==1 and b.id==0x28 and b.x==3272 and b.y==64 and b.y_high==1
   and b.camera_left>=2985 and b.camera_left<=3016 and b.camera_right-b.camera_left==255
   and v.frame>b.frame and v.camera_left>=b.camera_left and v.camera_right-v.x>=0
   and v.camera_right-v.x<=3 and v.x+15>=v.camera_left)
 local blocked=not b and windowStarted and windowExited and not badCamera
   and scanFirst and scanFirst.camera_left<2985 and scanLast and scanLast.camera_left>3016
   and searches>0 and searches==fullSearches and #keys(searchLeft)==#keys(seenLeft)
 local assisted=entered and firstCarry~=nil and departure~=nil and maxX>3288
 local passed=reason=='active-3-3' and entered and (C.released==1 or assisted)
   and losses==0 and not deathSeen and identity()
 shot('terminal')
 local receipt={passed=passed,reason=reason,ROM_sha256=C.rom,controller_only=true,script_RAM_writes=false,
   start_level_override=0x29,all_other_cheats_off=r('CheatInvincible')==0,menu_events=menuEvents,
   first_active=firstActive,terminal=state(),initial_lives=firstLives,life_decreases=losses,
   death_engine_seen=deathSeen,max_player_x=maxX,max_camera_left=maxCamera,progress=progress,
   entry_witness_passed=entered,capacity_blocked_witness=not not blocked,assisted_crossing=assisted,
   stage_exit=reason=='active-3-3',first_birth=b,physical_native_constructor_count=births,
   first_visible=v,first_carry=firstCarry,last_carry=lastCarry,native_carry_calls=carries,
   native_moving_carry_calls=movingCarries,first_departure=departure,board_attempt=boarding,
   lost_before_entry=lossBeforeVisible,camera_inconsistent=badCamera,screenshots=screenshots,
   slot_window={easy_left_start=2985,easy_left_end=3016,first_scan=scanFirst,last_scan=scanLast,
     observed_camera_left=keys(seenLeft),actual_allocator_camera_left=keys(searchLeft),
     eligible_scan_count=eligibleScans,actual_allocator_searches=searches,full_searches=fullSearches,
     max_occupied_at_search=maxOccupied,last_search=searchLast,window_exited=windowExited,
     columns={'flag','id','state','world_x','y','y_high'},rows=scanRows,dropped_distinct_rows=dropped}}
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(receipt)..'\n');f:close()
 print('Scrooge 3-2 '..reason..' entry='..tostring(entered)..' full-slot='..tostring(blocked)..' carry='..carries..' maxX='..maxX)
 emu.stop(passed and 0 or 1)
end

local function observePlay()
 if not identity() then return finish('character-mode-or-cheat-changed') end
 local lives=r('NumberofLives')
 if lives<lastLives then losses=losses+1 end;lastLives=lives
 if r('GameEngineSubroutine')==11 then deathSeen=true end
 if losses~=0 or deathSeen then return finish('life-loss-or-native-death') end
 if active(8) and r('WorldNumber')==2 and r('LevelNumber')==2 and area()==0x20 then return finish('active-3-3') end
 if stage() then
  local s=state()
  if s.x>maxX then maxX=s.x;lastAdvance=age end
  maxCamera=math.max(maxCamera,s.camera_left)
  if windowStarted and s.camera_left>3016 then windowExited=true end
  if age%180==0 and #progress<56 then progress[#progress+1]=s end
  if birth and not visible then
   local a=actor(birth.slot)
   if not owns(birth.slot) or a[1]~=1 or a[2]~=0x28 or a[3]~=0x60 then lossBeforeVisible=true
   elseif a[4]<=s.camera_right and a[4]+15>=s.camera_left then
    visible={frame=frame,slot=birth.slot,x=a[4],y=a[5],camera_left=s.camera_left,camera_right=s.camera_right}
   end
  end
  if visible and owns(visible.slot) then
   local a=actor(visible.slot)
   if a[4]<=s.camera_right-12 and a[4]+15>=s.camera_left then shot('visible-helper') end
  end
  if firstCarry then
   shot('boarded-helper')
   if not departure and frame-lastCarry.frame>=4 and s.x>math.max(lastCarry.helper_x+15,3288) then departure=s end
  end
  if active(8) and age-lastAdvance>=900 then return finish('controller-stationary-bound') end
 end
 if age>=10000 then return finish('physical-frame-bound') end
end

emu.addEventCallback(function()
 frame=frame+1;age=age+1
 if phase=='menu' then
  if menuWait>0 then menuWait=menuWait-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);menuWait=n or 0
 elseif phase=='handoff' then
  if active(8) and stage() then
   assert(identity(),'Real active Easy Scrooge 3-2 with only Start Level selected')
   firstActive=state();firstLives=firstActive.lives;lastLives=firstLives;phase='play';age=0
   assert(firstLives==2,'Start with two native lives counter')
  elseif age>=1000 then finish('no-real-3-2-handoff') end
 else observePlay() end
end,emu.eventType.endFrame)
