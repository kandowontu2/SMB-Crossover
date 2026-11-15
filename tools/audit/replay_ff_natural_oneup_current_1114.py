"""Strict571 per-class FF natural M/hidden1UP; frozen physicalv5 foundation."""
from functools import lru_cache
from hashlib import sha256
import re

import current_ff_stock_input_1114 as Current
import replay_dk_full11_roof_score_current_1114 as Boundary
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN=Current.R,Current.ROM,Current.PIN
W,N=Current.White,Current.White.N
TEMPLATE=R/'tools/playthroughs/ff_full_stage_stdout_1110_v5.lua'
TEMPLATE_SHA='aa18b8bcf1b81bbd817e507d1228a5f889dfea09cf73015c68f93de2c8fa4025'
IDENTITIES={'fighter-life':0,'white-life':1,'black-life':2,'thief-life':3}
NAMES=('FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF')


class Frozen:
    LuaRuntime=LuaRuntime
    lua=staticmethod(Boundary.Frozen.lua)


def normalize(raw):return Boundary.normalize(raw)


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=4)
def bindings(raw,key='fighter-life'):
    assert key in IDENTITIES;_,info=Current.bind(raw,kind=Current.KIND)
    source=TEMPLATE.read_bytes();assert sha256(source).hexdigest()==TEMPLATE_SHA
    text=source.decode();b=dict(W.Symbols.bundle(),raw=raw)
    literals=dict((n,int(v,16))for n,v in re.findall(r'(\w+)=0x([0-9a-f]+)',text.split('local L = {',1)[1].split('\n}',1)[0]))
    for name,value in literals.items():assert W.address(b,name)==value,('Current FF literal symbol',name,value,W.address(b,name))
    extra={name:W.address(b,name)for name in('StarInvincibleTimer','AreaMusicQueue','IntervalTimerControl','FfLife','FfReady','FloateyNum_Timer')}
    at=W.location(b,'FloateyNumbersCore');pc=W.address(b,'FloateyNumbersCore');bank=(at-16)//8192
    life=W.address(b,'NumberofLives');queue=W.address(b,'Square2SoundQueue')
    code=bytes((0xee,life&255,life>>8,0xa9,0x40,0x8d,queue&255,queue>>8))
    hits=[i for i in range(120)if raw[at+i:at+i+8]==code];assert len(hits)==1
    hooks={}
    for name,delta in(('LifeCreditBefore',hits[0]),('LifeCreditAfter',hits[0]+8)):
        hooks[name]=dict(pc=pc+delta,bank=bank,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]))
    variant=IDENTITIES[key]
    return dict(sha=PIN,key=key,variant=variant,name=NAMES[variant],slot=21,owner=22,cycle=variant,
        navigation=[4,4,1,1,1,1,1]+[32]*variant,extra_ram=extra,extra_hooks=hooks,
        cookie=list(bytes.fromhex(info['FF_cookie'])),worker_SHA256=info['FF_worker_SHA256'],binding=info)


@lru_cache(maxsize=4)
def controller(raw,key='fighter-life'):
    q=bindings(raw,key);text=TEMPLATE.read_text()
    text=once(text,"local variant = tonumber(env('SMB_TEST_VARIANT') or '0')",'local variant=C.variant')
    text=once(text,"local rom = env('SMB_STDOUT_ROM_SHA') or ''","local rom=C.sha\nassert(CPU_CONTROLLER_OPENING or env('SMB_STDOUT_ROM_SHA')==C.sha,'Explicit current571 FF input')")
    text=once(text,"local expectedStair = env('SMB_EXPECT_STAIR_STALL') == '1'",'local expectedStair=false')
    text=once(text,"local wantImages = env('SMB_STDOUT_IMAGES') == '1'",'local wantImages=false')
    text=once(text,'local frame, updates, completed, polls = 0, 0, 0, 0',
        'for n,a in pairs(C.extra_ram)do L[n]=a end\nlocal stock={resume=0};local stockCreditPending\nlocal frame, updates, completed, polls = 0, 0, 0, 0')
    text=once(text,'freeze_age=r(\'GuestPowerupAge\'), timer=r(\'TimerControl\'),',
        "freeze_age=r('GuestPowerupAge'), timer=r('TimerControl'),star=r('StarInvincibleTimer'),life_lease=r('FfLife'),")
    text=once(text,'active_1_2=active12, first_active_1_1=firstCold,','stock_oneup=stock,active_1_2=active12, first_active_1_1=firstCold,')
    text=once(text,"assert(s.lives==2,'Lost a life')", "assert(s.lives==(stock.credit and 3 or 2),'Actual initial or credited life count')")
    text=once(text,"assert(r('PlayerOutlinesOff')==1,'Natural cold extra-outline option changed')",
        "if not CPU_CONTROLLER_OPENING then assert(r('PlayerOutlinesOff')==1,'Natural cold extra-outline option changed')end")
    text=once(text,"validateGroup(1); enterPhase('flower'); transition=true", "validateGroup(1); enterPhase('stock-life'); transition=true")
    branch=r'''
  elseif phase=='stock-life'then
   assert(step<1800 and active(s),'Bounded active natural1UP continuation')
   assert(s.power==1 and s.earned==1 and s.charges==(variant==1 and 1 or 0),'Keep individually earned class gear')
   if stock.collected then
    bits=0
    if stock.credit then
     stock.resume=stock.resume+1
     if stock.resume==25 then
      assert(s.lives==3 and s.life_lease==3,'Native FF lease observes earned life')
      requestFinish(true,'Natural FF mushroom/hidden1UP/native credit and25 resumed calls');return
     end
    end
   elseif item then
    assert(item.kind==3,'Actual hidden-block kind3')
    stock.born=stock.born or{player=s,actor=item}
    if item.state>=128 then stock.mature=stock.mature or{player=s,actor=item}end
    local gap=item.x-s.x;bits=(gap>3 and 1 or 0)|(gap< -3 and 2 or 0)
    if math.abs(gap)<40 and item.y<s.y-16 and s.state==0 and step-(stock.jump or -100)>40 then
     bits=bits|128;stock.jump=step;desiredJumpReason='stock-life-item-jump'
    end
   elseif s.x<1016 then
    bits=1
    if s.state==0 and step-(stock.jump or -100)>40 then
     local obstacle
     for _,left in ipairs({448,608,736,912})do if not(stock.pipes or{})[left]and left-50<=s.x and s.x<left-3 then obstacle=left;break end end
     if obstacle then
      stock.pipes=stock.pipes or{};stock.pipes[obstacle]=true;stock.jump=step;bits=bits|128;desiredJumpReason='stock-life-pipe-'..obstacle
     end
    end
   else
    local gap=1018-s.x;bits=(gap>2 and 1 or 0)|(gap< -2 and 2 or 0)
    if math.abs(gap)<=2 and s.state==0 and step-(stock.jump or -100)>40 then
     stock.jump=step;bits=bits|128;desiredJumpReason='stock-life-hidden-block'
    end
   end
'''
    text=once(text,"  elseif phase=='flower' then",branch+"  elseif phase=='flower' then")
    install=r'''
 local function currentHook(name,fn)
  local h=C.extra_hooks[name]
  hook(h.pc,function(pc)return native(pc,h.bank)end,name,function(cpu)
   for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact current native stock hook')end;fn(cpu)
  end)
 end
 local bindingChecked=false
 hook(0xaabc,private,'CurrentFFWorker',function()
  if not gameplay or bindingChecked then return end
  assert(r('FfReady')==247,'Actual cold FF ready')
  for i,v in ipairs(C.cookie)do assert(emu.read(3*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Complete current FF cookie')end
  bindingChecked=true
 end)
 hook(0xbb60,private,'StockFfHostCollect',function(cpu)
  if not gameplay or phase~='stock-life'then return end
  local i=cpu['cpu.x'];local a=actor(i)
  assert(stock.born and stock.mature and a.flag==1 and a.id==46 and a.kind==3 and a.state>=128,'Actual mature named-class1UP collector')
  local before={player=state(),actor=a,slot=i};stock.collector=before
  onReturn(cpu,'stock-life-collect',before,function(q,returned)
   local p=returned['cpu.ps']or returned['cpu.p'];local s=state()
   assert(p&1~=0 and r('Enemy_Flag',q.slot)==0 and r('FloateyNum_Control',q.slot)==11 and r('Square2SoundQueue')==32,'Real native FF1UP erase/popup11/cue32')
   assert(s.active==0 and s.timer==0 and s.lives==2 and s.power==q.player.power and s.earned==q.player.earned and s.charges==q.player.charges,'1UP preserves class gear without freeze')
   stock.collected={before=q,after=s};stock.slot=q.slot
  end)
 end)
 currentHook('LifeCreditBefore',function(cpu)
  if not stock.collected or stock.credit or cpu['cpu.x']~=stock.slot then return end
  assert(cpu['cpu.y']==11 and r('FloateyNum_Control',stock.slot)==11 and r('FloateyNum_Timer',stock.slot)==42 and r('NumberofLives')==2,'Actual native popup11 credit ingress')
  stockCreditPending={player=state(),slot=stock.slot,timer=42}
 end)
 currentHook('LifeCreditAfter',function()
  if not stockCreditPending then return end
  assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual native INC life and cue64')
  stock.credit={before=stockCreditPending,after=state(),cue=64};stockCreditPending=nil
 end)
'''
    text=once(text," hook(0x82d9,function(pc) return native(pc,126) end,'GameLoop'",install+"\n hook(0x82d9,function(pc) return native(pc,126) end,'GameLoop'")
    start=text.index(" emu.addMemoryCallback(guarded('entrance priority'")
    end=text.index(" emu.addEventCallback(guarded('inputPolled'",start)
    text=text[:start]+text[end:]
    marker='local task=coroutine.create(function()'
    text=once(text,marker,marker+r'''
 if CPU_CONTROLLER_OPENING then
  assert(r('SelectedCharacter')==22 and r('FfVariant')==variant,'Actual compiled FF class menu')
  gameplay=true;enterPhase('mushroom');drive();while not stopped do coroutine.yield()end;return
 end''')
    start=text.index('  while #imageQueue>0 do');end=text.index('  if requestedFinish then',start)
    text=text[:start]+text[end:]
    text='local C='+Frozen.lua(q)+'\n'+text
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='fighter-life'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,class_name=q['name'],variant=q['variant'],controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        frozen_physical_v5_SHA256=TEMPLATE_SHA,FF_worker_SHA256=q['worker_SHA256'],FF_cookie=bytes(q['cookie']).hex(),
        normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='Named-class genuine M/freeze/resume then mature hidden1UP/native popup11/life2-to3/cue/+25; no sibling transfer, full stage or Star claim')
