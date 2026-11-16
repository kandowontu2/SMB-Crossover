"""Separate Mini real-M prefix, existing fixed lifts and genuine hidden1UP."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_mushroom_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='5f5f803b71146d6e48e909fd2fa60be4fec6d41daed326a45ce10ccb41e3772e'
BASE_TEMPLATE='26d7bb1f1d47a452b941e58c3003cd47aeae366dc2a095fc13e67496ec4fca06'
LIFT=R/'tools/playthroughs/mini_native_lifts_11_1108.lua'
LIFT_SHA='448e03682f320c8857e8c7589376256e92afae3edbd3587368e95afbfbea028e'


def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(Previous.__file__).read_bytes())==BASE_SHA and H(Previous.TEMPLATE.read_bytes())==BASE_TEMPLATE
    c=deepcopy(Previous.bindings(raw));c.update(kind='oneup',stock_type=3,target_x=1024,target_y=128);b=Current.bindings(raw)['bundle']
    for n in('AreaNumber','AreaType','Enemy_BoundBoxCtrl'):c['ram'][n]=W.address(b,n)
    def add(name,pc,at):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    add('InitEnemyObject',W.address(b,'InitEnemyObject'),W.location(b,'InitEnemyObject'))
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');life=c['ram']['NumberofLives'];cue=c['ram']['Square2SoundQueue']
    needle=bytes((0xee,life&255,life>>8,0xa9,64,0x8d,cue&255,cue>>8));hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    add('LifeBefore',pc+hits[0],at+hits[0]);add('LifeAfter',pc+hits[0]+len(needle),at+hits[0]+len(needle));return c


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(LIFT.read_bytes())==LIFT_SHA
    _,body=Previous.controller(raw).split('\n',1)
    body=once(body,"local function score()", "local M=item;local route={births={},support={}};local stockEndpoint\nlocal phases={fullstage={}};local L=C.ram;local ram=work;local updates=0\nlocal function supported(s)return s.class==2 and s.contacts&1~=0 end\nlocal function score()")
    body=once(body,"kind='mushroom'","kind=C.kind")
    body=once(body,'item=item,readback=readback','M=M,item=item,route=route,readback=readback')
    body=once(body,"r('NumberofLives')==2 and r('GameEngineSubroutine')~=11","r('NumberofLives')==(item.life_credit and 3 or 2)and r('GameEngineSubroutine')~=11")
    body=once(body,"a.id==46 and a.kind==0 then","a.id==46 and a.kind==(M.scope_passed and C.stock_type or 0)then")
    body=once(body,"assert(a.x>=280 and a.x<=440,'First authored Mushroom');if not item.born then assert(a.x==336);item.born={state=state(),actor=a}end", "if not item.born then assert(a.x==(M.scope_passed and C.target_x or 336),'Actual authored item column');item.born={state=state(),actor=a}end")
    body=once(body,'local function drive()',LIFT.read_text()+"\nlocal route_index=1;local route_obstacles={{left=448,right=480,top=176},{left=608,right=640,top=160},{left=736,right=768,top=144},{left=912,right=944,top=144}}\nlocal function drive()")
    body=once(body,'local a=observe();if item.collected then buttons={};return end',"local a=observe();if item.collected then buttons={};return end\n if M.scope_passed then\n  local s=state();local x,y=s.sourceX16/16,s.sourceY16/16;updates=steps\n  local slot=work(0xc30d)-1\n  if slot>=0 and slot<6 then local e=actor(slot);if e.flag==1 and e.id==37 then\n   local key=tostring(e.x);local row=route.support[key]or{slot=slot,left=e.x,samples=0,moving_matches=0};route.support[key]=row;row.samples=row.samples+1\n   if row.last and e.y~=row.last.top and s.y-row.last.y==e.y-row.last.top then row.moving_matches=row.moving_matches+1;row.first_motion=row.first_motion or{before=row.last,after={state=s,top=e.y}}end\n   row.last={y=s.y,top=e.y,Main=mains,step=steps};row.first=row.first or{state=s,actor=e}\n  end end\n  if item.phase=='travel'and x<960 then\n   local ob=route_obstacles[route_index];if ob and x>=ob.right+8 then route_index=route_index+1;ob=route_obstacles[route_index]end\n   local lift=mini_lift_inputs(s,ob,x);if lift then buttons=lift;return end\n   local floor=s.class==2 and s.contacts&1~=0\n   local want=solid(math.floor(x+24),math.floor(y+1))or solid(math.floor(x+24),math.floor(y+7))or not solid(math.floor(x+22),math.floor(y+8))or nearbyEnemy(x,y)\n   buttons={right=true,b=true};if s.queued==12 then buttons.a=true elseif floor then buttons.a=want and s.held&128==0 else buttons.a=true end;return\n  end\n  if item.phase=='travel'then item.phase='brake';item.since=steps end\n  assert(steps-item.since<450,'One original hidden-item admission/collection')\n  if a then item.phase='collect'end\n  if item.phase=='brake'then buttons={};if s.vx==0 and supported(s)and s.held&128==0 then item.phase='runup'end\n  elseif item.phase=='runup'then\n   buttons={right=true,b=true};if x>=C.target_x-32 and supported(s)and s.held&128==0 then item.phase='bump';item.takeoff=state();item.jump_since=steps;buttons.a=true end\n  elseif item.phase=='bump'then buttons={right=true,b=true,a=steps-item.jump_since<40};assert(steps-item.jump_since<100,'One real runjump must release hidden1UP')\n  elseif item.phase=='collect'then buttons=a and{right=x<a.x+1,left=x>a.x+7}or{}end\n  return\n end")
    body=once(body,'local function endpoint()\n','local function endpoint()\n if M.scope_passed then stockEndpoint();return end\n')
    body=once(body,"finish(true,'Natural Mini mature Mushroom/wholeC1/1000/60growth/25 real MiniStep+public returns')", "M.scope_passed=true;M.earned=state();item={phase='travel',power_updates=0,native_pickups=0,primary_leaf_entries=0,private_power_entries=0,vector24_entries=0};buttons={}")
    body=once(body,"a.id==46 and a.kind==0 and a.flag==1", "a.id==46 and a.kind==(M.scope_passed and C.stock_type or 0)and a.flag==1")
    body=once(body,"r('FloateyNum_Control',5)==6);item.collected", "r('FloateyNum_Control',5)==(M.scope_passed and 11 or 6));item.collected")
    extra="""stockEndpoint=function()
 if pendingMain or pendingMove or pendingStep or pendingCollect or pendingLeaf or pendingScore or pendingPower or not item.credit then return end
 item.resumed_steps=steps-item.credit.steps;item.resumed_moves=moves-item.credit.moves
 assert(item.resumed_steps<=25 and item.resumed_moves<=25)
 if item.resumed_steps==25 and item.resumed_moves==25 then
  identity();assert(item.born and item.mature and item.collected and item.erase and item.setup and item.sound32>0 and item.life_credit)
  assert(item.native_pickups==1 and item.primary_leaf_entries==1 and item.leaf_return.C==1 and r('NumberofLives')==3 and r('PlayerStatus')==1 and work(0xc244)==1,'Real life gain retains earned tier')
  assert(mainEntries==mains and moveEntries==moves and stepEntries==steps)
  item.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()};finish(true,'Natural Mini M then maturehidden1UP/wholeC1/realINC/cue64/25 original+public returns')
 end
end
hook('LifeBefore',function()if M.scope_passed and item.collected and not item.life_credit then local z=emu.getState();if z['cpu.x']==5 and r('FloateyNum_Control',5)==11 then assert(r('NumberofLives')==2 and z['cpu.y']==11);item.life_before={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state()}end end end)
hook('LifeAfter',function()if item.life_before and not item.life_credit then assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64);item.life_credit={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()};item.credit={steps=steps,moves=moves,state=state()}end end)
hook('InitEnemyObject',function()
 if not menuDone or r('SelectedCharacter')~=41 then return end;local z=emu.getState();local i=z['cpu.x'];local a=actor(i)
 if a.id~=37 or(a.x~=560 and a.x~=688 and a.x~=864)then return end
 local row={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),slot=i,stage=tostring(r('WorldNumber')+1)..'-'..tostring(r('LevelNumber')+1),area=r('AreaNumber'),initial_left=a.x,initial_center=a.x+16,initial_top=a.y,width=32};route.births[#route.births+1]=row
 returning(function(t)row.returned={PC=t.pc,SP=t.sp,actor=actor(i)}end)
end)
"""
    body=once(body,"hook('GameLoop',function()",extra+"hook('GameLoop',function()")
    body=once(body,"frame<7000 and mainEntries<2200,'Bounded natural Mini first Mushroom'", "frame<14000 and mainEntries<4200,'Bounded natural Mini M/hidden1UP'")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    return dict(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_M_factory_SHA256=BASE_SHA,parent_M_template_SHA256=BASE_TEMPLATE,facade_SHA256=Previous.CURRENT_SHA,grant_SHA256=Previous.GRANT_SHA,lift_input_SHA256=LIFT_SHA,scope='Actual1327 frozen genuine M prefix then existing fixed native lifts and ordinary runjump to authoredhiddenL; maturephysicalwholeC1/INC/cue64/+25 actualMiniStep+public returns',outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
