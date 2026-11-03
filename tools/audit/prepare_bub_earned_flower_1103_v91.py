"""Controller-only mushroom then later flower, using original bubble riding."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v91'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-initial-tier-native-1103-v88/bub-mushroom/controller.lua';text=source.read_text()
    needle='local function full_tick(finish)';assert text.count(needle)==1;text=text.replace(needle,'local function mushroom_tick(finish)')
    needle='  local obs=BUB_OBSERVER.finish();assert(obs.passed and obs.failures==0)';assert text.count(needle)==1
    text=text.replace(needle,'  local obs=BUB_OBSERVER.summary();assert(obs.failures==0)')
    wrapper='''
local flower_phase,flower_age,flower_last='mushroom',0,-1
local flower_target,flower_runup,flower_launch_base=nil,nil,nil
local flower_immature,flower_mature=false,false
local flower_csv=assert(io.open(OUTPUT..'flower.csv','w'))
flower_csv:write('Main,phase,x,y,native_state,source_state,flags,engine,target_x,target_y,item_state,item_x,item_y,rides\\n')
local function flower_change(p)flower_phase=p;flower_age=0;print('BUB_FLOWER_PHASE '..p..' x='..full_x()..' y='..r('Player_Y_Position'))end
local function full_tick(finish)
 if flower_phase=='mushroom'then
  return mushroom_tick(function()
   full_last=BUB_OBSERVER.summary().completed_Main;full_part='approach';full_step=0;full_pad={}
   flower_change('travel')
  end)
 end
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local engine=r('GameEngineSubroutine')
 local actor=Q.launch.bob==1 and 0x42 or 0x2e;local flags=full_state(actor+2);local item=upgrade_item()
 assert(r('NumberofLives')==2 and engine~=11,'Both earned upgrades require no death')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Flower required in actual1-1')
 if q.completed_Main~=flower_last then
  flower_last=q.completed_Main;flower_age=flower_age+1
  flower_csv:write(table.concat({q.completed_Main,flower_phase,x,y,r('Player_State'),full_state(actor+3),flags,engine,flower_target and flower_target.x or -1,flower_target and flower_target.y or -1,item and item.state or -1,item and item.x or -1,item and item.y or -1,q.source_bubble_ride_restarts},',')..'\\n');flower_csv:flush()
 end
 assert(flower_age<1200,'Bounded flower phase '..flower_phase)
 if item then
  assert(ram(L.PowerUpType+item.slot)==1,'Second actual power block releases flower')
  if item.state<128 then flower_immature=true;assert(flags==1,'Flower cannot upgrade before maturity')else flower_mature=true end
 end
 if engine==9 then full_pad={};return end
 if flags==7 and r('GuestPowerupActive')==0 and engine==8 then
  assert(r('PlayerStatus')==2 and flower_immature and flower_mature,'Genuine mature flower and completed native transformation')
  assert(flower_launch_base and q.source_bubble_ride_restarts>flower_launch_base.source_bubble_ride_restarts,'Flower reached using earned original bubble support')
  local obs=BUB_OBSERVER.finish();assert(obs.passed and obs.failures==0)
  local f=assert(io.open(OUTPUT..'earned-flower.json','w'));f:write(BUB_OBSERVER.json({passed=true,controller_only=true,ROM_sha256=BUB_NATIVE_OBSERVER_CONFIG.ROM_sha256,identity=Q.launch.bob,source_flags=flags,native_status=r('PlayerStatus'),lives=r('NumberofLives'),target=flower_target,observed_immature=flower_immature,observed_mature=flower_mature,observer=obs})..'\\n');f:close()
  flower_csv:close();shot('earned-flower-complete');finish();return
 end
 if flower_phase=='travel'then
  if not flower_target then
   local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
   for wx=math.floor(math.max(camera,1104)/16)*16,math.min(camera+224,x+160,1800),16 do
    for yy=80,160,16 do local _,tile=full_solid(wx+4,yy)
     if tile==0xc1 and(not flower_target or wx<flower_target.x)then flower_target={x=wx,y=yy}end
    end
   end
  end
  assert(x<1900,'Later flower block must be discovered before1900')
  if flower_target and x>=flower_target.x-32 and y>=flower_target.y+16 and r('Player_State')==0 then flower_change('align');full_pad={}
  else return full_tick_base(finish)end
 end
 if flower_phase=='align'then
  full_pad={right=x<flower_target.x+1,left=x>flower_target.x+3}
  if x>=flower_target.x+1 and x<=flower_target.x+3 and r('Player_State')==0 and full_state(0x301)&128==0 then flower_change('bump');full_pad={a=true}end
 elseif flower_phase=='bump'then
  full_pad={a=flower_age<25}
  if item then
   local left=flower_target.x
   for _=1,8 do if full_solid(left-12,flower_target.y)then left=left-16 else break end end
   flower_runup=math.max(left-96,1144)
   assert(flower_target.x<1376,'First later flower before next pit')
   flower_change('mount');full_pad={}
  elseif flower_age>80 then error('Original head must release second flower block')end
 elseif flower_phase=='mount'then
  if r('Player_State')~=0 or full_state(actor+3)~=0 then full_pad={};return end
  if x>flower_runup+2 then full_pad={left=true}
  elseif x<flower_runup-2 then full_pad={right=true}
  elseif full_state(0x102+(Q.launch.bob==1 and 8 or 0))&64==0 then full_pad={right=true}
  elseif full_launch_ready(actor)and full_state(0x301)&128==0 and flower_mature then
   flower_launch_base=q;flower_change('grow');full_pad={right=true,b=true}
  else full_pad={}end
 elseif flower_phase=='grow'then
  full_pad={right=true,b=flower_age<4}
  if flower_age>=5 then assert(q.launches>flower_launch_base.launches,'Original flower-mount bubble must launch')end
  local px=full_state(0x103+(Q.launch.bob==1 and 8 or 0))
  for i=0,14 do local gap=full_state(0x18b+8*i)-px
   if full_state(0x88+4*i)==2 and gap>=0 and gap<=24 then flower_change('ride');full_pad={right=true,a=true};break end
  end
  assert(flower_age<160,'Original flower bubble must grow into takeoff window')
 elseif flower_phase=='ride'then
  local tx=item and item.x or flower_target.x
  full_pad={right=x<tx-2,left=x>tx+3,a=true}
  if y<=flower_target.y-32 and r('Player_State')==0 then full_pad.a=false end
 end
end
'''
    marker="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert text.count(marker)==1;text=text.replace(marker,wrapper+'\n'+marker)
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-initial-tier-1103-v87/proposal.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Private controller-only earned firstmushroom then actual laterC1 flower block. Retains source/native/hardware guards, no life loss, actual emergence/maturity and native transformations; navigate with original speed upgrade and use original free-bubble support to reach stationaryflower. Bounded aggregateCSV, fourPNG maximum, no emulated writes or installation. Parent expandedISR qualification pending.')
if __name__=='__main__':main()
