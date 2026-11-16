"""Start the genuine held-grab jump on the higher existing first roof."""
from functools import lru_cache
import replay_prince_oneup_stage2_grab67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='a7c504067a27989fc74ad0f1097f54c1b0d808aff3d75b8492b7f0b7b0108ff6'
    old="stock.platform_wait_done=s;stockPhase('two1-platform-left',2)"
    assert text.count(old)==1;text=text.replace(old,"stock.platform_wait_done=s;stockPhase('two1-roof-A-ready',0)",1)
    old=" elseif stock.phase=='two1-platform-left'then"
    new=""" elseif stock.phase=='two1-roof-A-ready'then
  pad=0
  if idle(s)and s.action==0 then
   assert(s.y>=111 and s.y<=114 and s.facing==255,'Actual higher roof idle before fresh held-grab jump')
   stock.stair_jumps={{request=s,foot_cells={tile(s.x+3,s.foot),tile(s.x+12,s.foot)}}}
   stockPhase('two1-roof-A',128)
  end
  assert(age<160,'Actual original roof action0 before A')
 elseif stock.phase=='two1-roof-A'then
  pad=128
  if s.action==3 then
   local j=stock.stair_jumps[1];j.admission=s;j.minimum_y=s.y;j.samples={}
   stock.stair_advance=stock.prince_returns;stock.stair_max=s.x
   stockPhase('two1-stair-air',129)
  end
  assert(age<90,'Original standing jump3 admission on higher existing roof')
 elseif stock.phase=='two1-platform-left'then"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        original_F89B_grab_gate_authenticated=True,actual_first_roof_fresh_A3_then_RightA=True,
        Up_only_after_actual_hang=True,real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
