"""Release the actual careful step before one ordinary cap running jump."""
from functools import lru_cache
import replay_prince_hidden_fullcap_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change("stockPhase('cap-run',1)","stockPhase('cap-ready',0)")
    change(" if stock.phase=='ground-retreat'then",r''' if stock.phase=='cap-ready'then
  pad=0
  if age>=8 and idle(s)and s.action==0 then
   local left,right=capFeet(s,912,144);assert(left and right,'Actual full-cap fresh idle before runway')
   stock.cap_ready=s;stockPhase('cap-run',1)
  end
  assert(age<160,'Bounded actual careful-step release on cap')
 elseif stock.phase=='ground-retreat'then''')
    Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        genuine_full_cap_then_action0_release=True,ordinary_running_A_then_Up=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
