"""Fresh original standing jumps from measured native staircase footholds."""
from functools import lru_cache
import replay_prince_oneup_stage2_stair67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='e96b11e20dc5a7f697eb00cce5f1e34749885db60da2b608eb13f70b3f412796'
    a=text.index(" elseif stock.phase=='two1-stair-settle'then")
    b=text.index(" elseif stock.phase=='coin-ledge-approach'then",a)
    text=text[:a]+r''' elseif stock.phase=='two1-stair-settle'then
  pad=0
  if idle(s)and s.action==0 then
   stock.stair_jumps=stock.stair_jumps or {}
   assert(#stock.stair_jumps<3,'At most three ordinary fresh standing jumps over actual stairs')
   stock.stair_jumps[#stock.stair_jumps+1]={request=s,foot_cells={tile(s.x+3,s.foot),tile(s.x+12,s.foot)}}
   stockPhase('two1-stair-A',128)
  end
  assert(age<160,'Actual idle at stair face before fresh standing A')
 elseif stock.phase=='two1-stair-A'then
  pad=128
  if s.action==3 then
   local j=stock.stair_jumps[#stock.stair_jumps];j.admission=s;j.minimum_y=s.y;j.samples={}
   stock.stair_advance=stock.prince_returns;stock.stair_max=s.x
   stockPhase('two1-stair-air',1)
  end
  assert(age<90,'Original standing jump3 admission at real stair support')
 elseif stock.phase=='two1-stair-air'then
  pad=s.x<400 and 1 or 0
  local j=stock.stair_jumps[#stock.stair_jumps];j.minimum_y=math.min(j.minimum_y,s.y)
  if #j.samples<14 and(#j.samples==0 or j.samples[#j.samples].pose~=s.pose)then j.samples[#j.samples+1]=s end
  if s.x>stock.stair_max then stock.stair_max=s.x;stock.stair_advance=stock.prince_returns end
  if s.x>=400 and idle(s)and s.action==0 then j.landing=s;stock.farbank=s;stockPhase('approach',0)
  elseif age>=24 and s.action==1 and s.mode==1 and stock.prince_returns-stock.stair_advance>=24 then
   j.wall=s;stockPhase('two1-stair-settle',0)
  end
  assert(age<240,'Bounded original standing-jump traversal of actual staircase')
'''+text[b:]
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        measured_staircase_then_fresh_original_standing_A3=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
