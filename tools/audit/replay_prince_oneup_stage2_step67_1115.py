"""One original careful step for the short roof, then fresh standing A3."""
from functools import lru_cache
import replay_prince_oneup_stage2_actor67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='79b6fca720bae82440f4674bb07de87834b250dd7910aa1fd1cae4e39bb51c0c'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    a=text.index(" elseif stock.phase=='two1-platform-left'then");b=text.index(" elseif stock.phase=='two1-platform-flight'then",a)
    text=text[:a]+r''' elseif stock.phase=='two1-platform-left'then
  pad=0
  if idle(s)and s.action==0 then stockPhase('two1-platform-face-left',2)end
  assert(age<160,'Actual idle before careful roof step')
 elseif stock.phase=='two1-platform-face-left'then
  pad=2;if s.facing==0 then stockPhase('two1-platform-face-settle',0)end
  assert(age<100,'Actual facing Left before original careful step')
 elseif stock.phase=='two1-platform-face-settle'then
  pad=0
  if idle(s)and s.action==0 then stock.step_start=#stock.step_decisions;stockPhase('two1-platform-one-step',66)end
  assert(age<160,'Actual turn completion before original step')
 elseif stock.phase=='two1-platform-one-step'then
  pad=66;if #stock.step_decisions>stock.step_start then stockPhase('two1-platform-step-settle',0)end
  assert(age<100,'Actual original partial/full/no-step decision')
 elseif stock.phase=='two1-platform-step-settle'then
  pad=0
  if idle(s)and s.action==0 then
   assert(math.abs(s.y-112)<=2,'Completed careful step retains actual roof height')
   stock.platform_runway=s;stockPhase('two1-platform-face-right',1)
  end
  assert(age<200,'Actual careful-step completion')
 elseif stock.phase=='two1-platform-face-right'then
  pad=1;if s.facing==255 then stockPhase('two1-platform-A-ready',0)end
  assert(age<100,'Actual facing Right for standing jump')
 elseif stock.phase=='two1-platform-A-ready'then
  pad=0
  if idle(s)and s.action==0 then stock.jump_request=s;stockPhase('two1-platform-A',128)end
  assert(age<160,'Actual neutral standing jump readiness')
 elseif stock.phase=='two1-platform-A'then
  pad=128
  if s.action==3 then stock.jump_admission=s;stockPhase('two1-platform-flight',1)end
  assert(age<90,'Actual original standing jump3 required')
'''+text[b:]
    change("if not stock.active or stock.phase~='fine-step'then return end",
        "if not stock.active or(stock.phase~='fine-step'and stock.phase~='two1-platform-one-step')then return end")
    old="stock.platform_idle=s;stockPhase('two1-platform-wait',0)"
    new="stock.platform_idle=s;stock.first_pit_geometry={};for x=304,432,16 do stock.first_pit_geometry[#stock.first_pit_geometry+1]={x=x,row208=tile(x,208)}end;stockPhase('two1-platform-wait',0)"
    change(old,new);LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        original_facing_and_one_careful_step_then_actual_standing_jump3=True,
        actual_roof_idle_and_first_pit_native_geometry_recorded=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
