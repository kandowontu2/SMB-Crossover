"""Original supported hidden-L pickup, including native legal early admission."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_manual_ctor_1327_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='455c7b479efcbfea5460439effb72902c0b37783d2e445a446c94d76367047a5'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    text=once(text,"local away=C.target_x-24;buttons={left=x>away+1,right=x<away-1}","buttons={}")
    text=once(text,"a.state>=128 and item.born and item.mature and not item.collected","(M.scope_passed and a.state>=6 or not M.scope_passed and a.state>=128)and item.born and(M.scope_passed or item.mature)and not item.collected")
    old=" local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',a.slot);"
    new=""" if M.scope_passed then
  assert(item.last_min6 and item.last_min6.state==a.state and a.state>=6,'Actual unchanged native state>=6 admission')
  item.admission={state=state(),actor=a,native_threshold=item.last_min6,full_maturity=a.state>=128}
 end
"""+old
    text=once(text,old,new)
    text=once(text,"assert(item.born and item.mature and item.collected and item.erase and item.setup and item.sound32>0 and item.life_credit)","assert(item.born and item.admission and item.admission.actor.state>=6 and item.collected and item.erase and item.setup and item.sound32>0 and item.life_credit)")
    text=once(text,"Natural Mini M then maturehidden1UP/wholeC1/realINC/cue64/25 original+public returns","Natural Mini M then original-admitted supportedhidden1UP/wholeC1/realINC/cue64/25 original+public returns")
    old="  if a then item.phase=a.state<128 and 'wait-mature'or'collect'end"
    new=old+"""
  if a then
   item.chase_samples=item.chase_samples or{}
   if #item.chase_samples<20 and(not item.chase_last or steps-item.chase_last>=8)then
    item.chase_last=steps;item.chase_samples[#item.chase_samples+1]={state=s,actor=a,player_box=box('BoundingBox_UL_Corner'),item_box=box('EnemyBoundingBoxCoord',a.slot)}
   end
  end"""
    text=once(text,old,new);LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_manual_ctor_SHA256=BASE_SHA,scope='Actual1327 genuine M; unchanged existing supports, stay during hiddenL emergence; original native >=6 actual physical admission/wholeC1/INC/cue64/+25; full128 maturation only if reached');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
