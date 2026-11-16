"""Legal pipe drop and ground running jump under the authored1UP; strict7fb."""
from functools import lru_cache
import replay_prince_hidden_point67_ace_1115 as Previous
import prince_oneup_return_observer_7fb_1115 as Return
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='461dd1ab6eb716e5510c6f36441425dfce36602f9b326716a2f1d7d0d0a095c9'
    old="stockPhase('cap-fresh-A',128)";assert text.count(old)==1
    text=text.replace(old,"stockPhase('ground-drop',1)",1)
    lo=text.index(" elseif stock.phase=='cap-fresh-A'then");hi=text.index(" elseif stock.phase=='ground-retreat'then",lo)
    body=r''' elseif stock.phase=='ground-drop'then
  pad=1
  if s.y>=175 and floor(s)then stock.ground_drop=s;stockPhase('ground-settle',0)end
  assert(age<240,'Bounded legal drop to actual ground')
 elseif stock.phase=='ground-settle'then
  pad=0
  if idle(s)and s.action==0 then stockPhase('ground-backup',2)end
  assert(age<160,'Actual ground landing returns to idle')
 elseif stock.phase=='ground-backup'then
  pad=2;if s.x<=STOCK.x-64 then stockPhase('ground-neutral',0)end
  assert(age<120,'Finite ordinary runway backup')
 elseif stock.phase=='ground-neutral'then
  pad=0
  if idle(s)and s.action==0 then stock.ground_ready=s;stockPhase('ground-run',1)end
  assert(age<160,'Actual ordinary runway idle')
 elseif stock.phase=='ground-run'then
  pad=1
  if s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then
   stock.running_request=s;stockPhase('ground-A',129)
  end
  assert(age<90,'Actual original ground running admission pose')
 elseif stock.phase=='ground-A'then
  pad=129
  if s.action==4 then stock.running_admission=s;stock.minimum_y=s.y;stockPhase('ground-flight',129)end
  assert(age<90,'Actual original ground action4 required')
 elseif stock.phase=='ground-flight'then
  stock.minimum_y=math.min(stock.minimum_y,s.y);pad=s.x<STOCK.x+16 and 129 or 0
  if age>100 and floor(s)and idle(s)and s.action==0 then
   stock.ground_landing=s;final=s;finish(false,'Ground running jump landed without hidden1UP birth')
  end
  assert(age<400,'Bounded original ground jump and landing')
'''
    text=text[:lo]+body+text[hi:]
    old="stock.phase~='standing-flight'";assert text.count(old)==3;text=text.replace(old,"stock.phase~='ground-flight'")
    text=Return.install(text);LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        legal_drop_and_actual_ground_running_action4=True,actual_head_query_trace_retained=True,
        genuine_birth_mature_overlap_delayed_INC_cue64_and25returns_required=True,
        completion_at_authenticated_Main_return=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
