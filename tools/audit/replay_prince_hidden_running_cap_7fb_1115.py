"""Ordinary cap walk to authentic donor running-jump admission; strict7fb."""
from functools import lru_cache
import replay_prince_hidden_point67_ace_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='461dd1ab6eb716e5510c6f36441425dfce36602f9b326716a2f1d7d0d0a095c9'
    old="stockPhase('cap-fresh-A',128)";assert text.count(old)==1
    text=text.replace(old,"stockPhase('cap-running-admit',1)",1)
    lo=text.index(" elseif stock.phase=='cap-fresh-A'then")
    hi=text.index(" elseif stock.phase=='ground-retreat'then",lo)
    body=r''' elseif stock.phase=='cap-running-admit'then
  pad=1;stock.running_approach=stock.running_approach or{}
  if #stock.running_approach<16 then stock.running_approach[#stock.running_approach+1]=s end
  local ready=s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0
  if ready then
   stock.running_request=s;stockPhase('cap-running-A',129)
  end
  assert(age<80,'Actual F473 running poses6..13 required before fresh A')
 elseif stock.phase=='cap-running-A'then
  pad=129
  if s.action==4 then
   stock.running_admission=s;stock.minimum_y=s.y
   stock.running_support={left_x=s.x+2,right_x=s.x+13,row=s.y+32,left_tile=tile(s.x+2,s.y+32),right_tile=tile(s.x+13,s.y+32),native_ground=s.ground,source_foot=s.foot}
   stockPhase('cap-running-flight',129)
  end
  assert(age<90,'Actual original running action4 admission required')
 elseif stock.phase=='cap-running-flight'then
  stock.minimum_y=math.min(stock.minimum_y,s.y);pad=s.x<1040 and 129 or 0
  if age>100 and floor(s)and idle(s)and s.action==0 then
   stock.running_landing=s;final=s;finish(false,'Original cap running jump landed without hidden1UP birth')
  end
  assert(age<400,'Bounded original running cap jump and landing')
'''
    text=text[:lo]+body+text[hi:]
    old="stock.phase~='standing-flight'";assert text.count(old)==3
    text=text.replace(old,"stock.phase~='cap-running-flight'")
    LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        source_running_gate_F473_poses6_to13=True,actual_action4_required=True,
        genuine_hidden_birth_mature_overlap_delayed_INC_cue64_and25actual_returns_required=True,
        ordinary_controls_only=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
