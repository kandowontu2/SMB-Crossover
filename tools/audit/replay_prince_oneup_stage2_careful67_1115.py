"""Original careful steps at real staircase contact, then actual roof A."""
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
   stock.stair_steps=stock.stair_steps or {}
   local previous=stock.stair_steps[#stock.stair_steps]
   if previous and not previous.completed then
    previous.completed=s
    assert(s.x>previous.request.x or s.y<previous.request.y,'Original careful stair step must make real progress')
   end
   if s.y<=98 and s.x>=384 then
    stock.stair_cap_idle=s;stock.request=s;stock.minimum_y=s.y;stock.attempts=stock.attempts+1
    stock.actual_head_pad=128;stockPhase('jump',128)
   else
    assert(#stock.stair_steps<6,'At most six original careful stair steps')
    stock.stair_steps[#stock.stair_steps+1]={request=s,decision_start=#stock.step_decisions,
     foot_cells={tile(s.x+3,s.foot),tile(s.x+12,s.foot)}}
    stockPhase('two1-stair-step',65)
   end
  end
  assert(age<180,'Actual idle after original careful staircase step')
 elseif stock.phase=='two1-stair-step'then
  pad=65
  local step=stock.stair_steps[#stock.stair_steps]
  if #stock.step_decisions>step.decision_start then step.decision=stock.step_decisions[#stock.step_decisions];stockPhase('two1-stair-settle',0)end
  assert(age<100,'Fresh original partial/full/no-step selector required')
'''+text[b:]
    old="if not stock.active or(stock.phase~='fine-step'and stock.phase~='two1-platform-one-step')then return end"
    new="if not stock.active or(stock.phase~='fine-step'and stock.phase~='two1-platform-one-step'and stock.phase~='two1-stair-step')then return end"
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        original_B_Right_careful_selector_fresh_decision_and_completion=True,
        actual_stair_roof_height_before_standing_head_jump=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
