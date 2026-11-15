"""Release the genuine Up mount, then test an early original running jump."""
from functools import lru_cache
import replay_prince_hidden_partial_up_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    old="""  if idle(s)and s.action==0 then
   local left,right=capFeet(s,912,144)
   if left and right then stock.actual_mount=s;stockPhase('cap-run',1)end
  end
  assert(age<240,'Bounded original partial-cap Up continuation')"""
    new=r'''  local left,right=capFeet(s,912,144)
  if left and right and s.action==8 then stock.actual_mount=s;stockPhase('cap-release',0)end
  assert(age<240,'Bounded original partial-cap Up continuation')
 elseif stock.phase=='cap-release'then
  pad=0
  if idle(s)and s.action==0 then
   local left,right=capFeet(s,912,144);assert(left and right,'Actual supported idle after Up mount release')
   stock.cap_ready=s;stockPhase('cap-run',1)
  end
  assert(age<200,'Bounded ordinary mounted reach release')'''
    change(old,new)
    # Original F46D latches an early A request; F473..F47D still require
    # poses6..13 before action4. Pressing earlier cannot bypass that gate.
    # Require the actual original action4 before continuing the route.
    change('local ready=s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0',
        'local ready=s.action==1 and s.mode==1 and s.pose>=0 and s.pose<=13 and s.lock==0')
    Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        genuine_partial_Up_mount_then_release=True,original_action1_then_A_and_action4_required=True,
        actual_delayed_life_cue64_and_25_Prince_returns_required=True,endpoint_at_actual_Main_return=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
