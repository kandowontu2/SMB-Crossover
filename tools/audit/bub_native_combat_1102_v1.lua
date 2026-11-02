-- Controller-only natural Goomba encounter. No emulated state is written.
BUB_NATIVE_OBSERVER_CONFIG.output=OUTPUT
local combat_part,combat_step,combat_last='approach',0,0
local combat_lives,combat_base,combat_target,combat_capture=nil,nil,nil,nil
local combat_events,combat_defeats={},0
local combat_maxx=0
local function worldx(i)
 if i then return ram(L.Enemy_X_Position+i)+256*ram(L.Enemy_PageLoc+i)end
 return r('Player_X_Position')+256*r('Player_PageLoc')
end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function source(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function geometry(i)
 local bubbles={}
 for n=0,14 do if source(0x88+4*n)~=0 then
  bubbles[#bubbles+1]={slot=n,flag=source(0x88+4*n),x=source(0x18b+8*n),y=source(0x188+8*n)}
 end end
 return{slot=i,ID=ram(L.Enemy_ID+i),flag=ram(L.Enemy_Flag+i),native_x=worldx(i),native_y=ram(L.Enemy_Y_Position+i),
  source_player_y=source(0x100),source_proxy_x=source(0x113+8*i),source_proxy_y=source(0x110+8*i),
  source_enemy_fields={source(0x68+4*i),source(0x69+4*i),source(0x6a+4*i),source(0x6b+4*i)},
  source_trap_clock=source(0x213),bubbles=bubbles}
end
local function target()
 local chosen,gap=nil,10000
 for i=0,5 do
  local f=ram(L.Enemy_Flag+i);local state=ram(L.Enemy_State+i)
  if f>0 and f<128 and ram(L.Enemy_ID+i)==6 and state&32==0 then
   local d=worldx(i)-worldx();if d>0 and d<gap then chosen,gap=i,d end
  end
 end
 return chosen,gap
end
local function combat_label()return phase=='combat'and combat_part or phase end
local function combat_keys()
 if combat_part=='approach'then return{'right'}end
 if combat_part=='fire'then return combat_step<4 and{'b'}or{}end
 if combat_part=='retreat'then return{'left'}end
 if combat_part=='wait-capture'then
  local _,gap=target();return gap<28 and{'left'}or{}
 end
 if combat_part=='pop-approach'then
  local keys={};local d=worldx(combat_target)-worldx()
  if d>4 then keys[#keys+1]='right'elseif d< -4 then keys[#keys+1]='left'end
  if combat_step<32 then keys[#keys+1]='a'end
  return keys
 end
 return{}
end
local function combat_event(kind,detail)
 assert(#combat_events<32,'Bounded combat phase aggregate')
 combat_events[#combat_events+1]={kind=kind,Main=BUB_OBSERVER.summary().completed_Main,
  x=worldx(),y=r('Player_Y_Position'),camera=camera(),detail=detail}
end
local function combat_phase(name,detail)
 combat_event(name,detail or{});combat_part=name;combat_step=0
end
local function combat_write(passed,why,source_summary)
 local q={passed=passed,why=why,controller_only=true,ROM_sha256=Q.ROM_sha256,
  mode=COMBAT_MODE,initial_lives=combat_lives,final_lives=r('NumberofLives'),
  source=source_summary,events=combat_events,actual_native_defeat_entries=combat_defeats,
  maximum_x=combat_maxx,helpers_added=false,full_stage=false,installed=false}
 local f=assert(io.open(OUTPUT..'earned-combat.json','w'));f:write(BUB_OBSERVER.json(q)..'\n');f:close()
end
local function combat_fail(why)
 local q=BUB_OBSERVER.finish();combat_write(false,why,q);assert(false,why)
end
local function combat_begin()
 assert(ppu(0x3f00)==0x22,'Correct native backdrop before earned combat')
 assert(r('SelectedCharacter')==39 and r('GameEngineSubroutine')==8)
 phase='combat';age=0;combat_lives=r('NumberofLives');combat_base=BUB_OBSERVER.summary()
 combat_last=combat_base.completed_Main;combat_maxx=worldx()
 combat_phase('approach');shot('natural-cold-spawn')
end
local defeat=BUB_NATIVE_OBSERVER_CONFIG.hooks.ShellOrBlockDefeat
emu.addMemoryCallback(function()
 if phase~='combat'then return end
 local a=emu.convertAddress(defeat.pc)
 if a and a.memType==emu.memType[defeat.memory]and a.address==defeat.physical then
  for i,v in ipairs(defeat.bytes)do assert(ram(defeat.pc+i-1)==v,'Actual native defeat preimage')end
  combat_defeats=combat_defeats+1
 end
end,emu.callbackType.exec,defeat.pc)
local function combat_tick(finish)
 if r('SelectedCharacter')~=39 or r('OperMode')~=1 or r('GameEngineSubroutine')~=8 or r('NumberofLives')~=combat_lives then combat_fail('Natural combat injured or lost the actual owner/life')end
 local q=BUB_OBSERVER.summary()
 if q.completed_Main==combat_last then return end
 assert(q.completed_Main==combat_last+1,'Actual combat Main observation cadence')
 combat_last=q.completed_Main;combat_step=combat_step+1;combat_maxx=math.max(combat_maxx,worldx())
 if q.completed_Main-combat_base.completed_Main>1400 then combat_fail('Global bounded natural encounter without earned result')end
 if combat_part=='approach'then
  local i,gap=target()
  if i and gap<=60 then
   if gap<28 then combat_fail('Natural Goomba reached unsafe distance before shot')end
   combat_target=i
   local g=geometry(i);g.gap=gap;combat_phase('fire',g)
  end
 elseif combat_part=='fire'and combat_step>=4 then
  if q.launches<=combat_base.launches then combat_fail('Fresh B did not create an original source bubble')end
  combat_phase('wait-capture',geometry(combat_target))
 elseif combat_part=='wait-capture'then
  if q.captures>combat_base.captures then
   local found=nil
   for i=0,5 do if source(0x320+16*i)~=0 then found=i;break end end
   assert(found~=nil,'Actual captured native association')
   combat_target=found
   combat_capture={Main=q.completed_Main,camera=camera(),flag=source(0x322+16*found),ID=source(0x321+16*found)}
   assert(combat_capture.ID==6,'Naturally parsed Goomba captured')
   shot('earned-original-trap')
   combat_phase(COMBAT_MODE=='timeout'and'retreat'or'pop-approach',geometry(found))
  elseif combat_step>=70 then combat_fail('Original fresh bubble did not capture natural Goomba within bound')end
 elseif combat_part=='retreat'and combat_step>=20 then combat_phase('wait-timeout')
 elseif combat_part=='wait-timeout'or combat_part=='pop-approach'then
  local wanted=COMBAT_MODE=='timeout'and q.releases>combat_base.releases or COMBAT_MODE=='pop'and q.pops>combat_base.pops
  if wanted then
   local elapsed=q.completed_Main-combat_capture.Main
   local f=ram(L.Enemy_Flag+combat_target);local state=ram(L.Enemy_State+combat_target)
   if COMBAT_MODE=='timeout'then
    assert(elapsed>=39 and camera()==combat_capture.camera,'Actual source timeout clock with unchanged camera')
    assert(f==combat_capture.flag and ram(L.Enemy_ID+combat_target)==combat_capture.ID and state&32==0,'Original positive native flag/ID restored after timeout')
   else
    assert(elapsed<40 and combat_defeats>0 and state&32~=0,'Earned source pop reaches actual native defeat before timeout')
   end
   local g=geometry(combat_target);g.elapsed_source_updates=elapsed;g.state=state
   combat_event('earned-'..COMBAT_MODE,g)
   local final=BUB_OBSERVER.finish();combat_write(final.passed,'earned-'..COMBAT_MODE,final)
   assert(final.passed,'Actual source/header/hardware combat observer')
   shot('earned-'..COMBAT_MODE);finish()
  elseif q.completed_Main-combat_capture.Main>=75 then combat_fail('Natural capture did not earn requested '..COMBAT_MODE..' within bound')end
 end
end
