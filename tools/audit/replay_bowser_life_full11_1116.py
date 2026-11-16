"""Separate exact6a3 genuine1UP then full1-1 controller; frozen item factory intact."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_bowser_life_gain_1116 as Previous

R,ROM,PIN,W,N,C,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.C,Previous.Current
PARENT_SHA='7db841a2828ae02ac3927f129fe72fa6da6c323700c3e870d38be11223ce7d7c'
CONTROL=R/'tools/playthroughs/bowser_life_full11_1116.lua'
once=Previous.Previous.once

@lru_cache(maxsize=2)
def controller(raw,identity=1):
    assert C.digest(Path(Previous.__file__).read_bytes())==PARENT_SHA
    text=Previous.controller(raw,identity,'oneup')
    text=once(text,"local stock={phase='travel',trace={}}", "local stock={phase='travel',trace={}}\nlocal full={phase='items',grounded_pairs=0,area_constructs={}}")
    text=once(text,"hook('BwConstruct',function()assert(not stock.credit,'Earned life must not invoke fresh construction')end)","""hook('BwConstruct',function()
 if stock.credit then
  local s=sample()
  assert(stock.full_handoff and flag and castle and s.world==0 and s.level==1,'Only genuine castle-to-next-area construction after earned life')
  full.area_constructs[#full.area_constructs+1]={s=s,pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 end
end)""")
    text=once(text,"    finish(true,'Natural Bowser '..BStock.key..' and25 original full-step/outer-tail returns at actual Main return')", """    stock.item_scope_passed=true
    stock.full_handoff={s=sample(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
    stock.active=false;full.phase='land-after-life';full.since=updates
    full.last_core=coreReturns;full.last_tail=tailReturns
    lastX=-1;still=0;hold=0;lastA=false;pad=0""")
    old=""" if s.world==0 and s.level==1 and s.area==2 and active()then
  nextUpdates=s.y==176 and nextUpdates+1 or 0
  if nextUpdates>=25 then
   assert(flag and castle and entrance,'Real native flagpole/castle/next-area chain')
   finish(true,'Bowser clears non-shortcut1-1 then25 grounded quiet underground1-2 updates');return
  end
  pad=0;return
 end"""
    new=""" if s.world==0 and s.level==1 and s.area==2 and active()then pad=0;return end"""
    text=once(text,old,new)
    text=once(text,'local function drive()','local function itemDrive()')
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    text=once(text,marker,CONTROL.read_text()+'\n'+marker)
    text=once(text,'natural=natural,stock=stock','natural=natural,stock=stock,full=full')
    Previous.Previous.Old.Base.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text

def metadata(raw,identity=1):
    q=Previous.metadata(raw,identity,'oneup');text=controller(raw,identity)
    q.update(controller_SHA256=C.digest(text.encode()),full_factory_SHA256=C.digest(Path(__file__).read_bytes()),
        full_controls_SHA256=C.digest(CONTROL.read_bytes()),scope='Real M/hiddenL/+25 item proof then full nonshortcut1-1 and25 livinggrounded completed core/tail pairs in1-2',
        frozen_item_factory_SHA256=PARENT_SHA,full_stage_claim_pending_source_or_native=True)
    return q

def family(identity=1):
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,identity),metadata=lambda raw,key:metadata(raw,identity))
