"""Continue from actual stair contact using original Up and height-aware head input."""
from functools import lru_cache
import replay_prince_oneup_stage2_step67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='da74ee1bb369c0e0642dd88404136e10aa59bfb85c524d838199dd31c2fe030d'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    a=text.index(" elseif stock.phase=='two1-platform-flight'then");b=text.index(" elseif stock.phase=='coin-ledge-approach'then",a)
    text=text[:a]+r''' elseif stock.phase=='two1-platform-flight'then
  pad=s.x<400 and 1 or 0
  if not stock.stair_max or s.x>stock.stair_max then stock.stair_max=s.x;stock.stair_advance=stock.prince_returns end
  if s.x>=400 and idle(s)and s.action==0 then stock.farbank=s;stockPhase('approach',0)
  elseif s.action==1 and s.mode==1 and s.y<=144 and stock.prince_returns-stock.stair_advance>=24 then
   stock.stair_contact=s;stock.stair_geometry={}
   for x=320,464,16 do local row={x=x};for y=80,208,16 do local t=tile(x,y);if t~=0 then row[#row+1]={y=y,tile=t}end end;stock.stair_geometry[#stock.stair_geometry+1]=row end
   stockPhase('two1-stair-settle',0)
  end
  assert(age<300,'Bounded ordinary approach to measured staircase contact')
 elseif stock.phase=='two1-stair-settle'then
  pad=0;if idle(s)and s.action==0 then stock.stair_ready=s;stockPhase('two1-stair-up',8)end
  assert(age<160,'Actual idle at stair face before Up')
 elseif stock.phase=='two1-stair-up'then
  pad=8
  if s.x>=400 and s.y<132 and s.foot<164 then stock.stair_raised=s;stockPhase('two1-stair-release',0)end
  assert(age<420,'Original Up advances past actual staircase face')
 elseif stock.phase=='two1-stair-release'then
  pad=0
  if idle(s)and s.action==0 then stock.stair_idle=s;stockPhase('approach',0)end
  assert(age<200,'Actual idle after stair climb')
'''+text[b:]
    # A standing state on a raised native roof is not the fixed ground176
    # predicate inherited from the Star's old approach. Gameplay still must
    # admit the input; all actor/credit/life/25-return gates remain intact.
    change("  if floor(s)and idle(s)and s.action==0 then\n   -- Actual native head adder8",
        "  if idle(s)and s.action==0 then\n   -- Actual native head adder8")
    change("if age>=8 and floor(s)and idle(s)and s.action==0 then stock.attempts=stock.attempts+1;assert(stock.attempts<=4,'Finite real hidden/block jump attempts');stock.request=s;stock.minimum_y=s.y;stockPhase('jump',STOCK.jump)end",
        "if age>=8 and idle(s)and s.action==0 then stock.attempts=stock.attempts+1;assert(stock.attempts<=4,'Finite real hidden/block jump attempts');stock.request=s;stock.minimum_y=s.y;local hy=s.y+1;stock.actual_head_pad=(hy>=STOCK.y+16 and hy<=STOCK.y+20)and 128 or 8;stockPhase('jump',stock.actual_head_pad)end")
    change('  pad=age<80 and STOCK.jump or 0','  pad=age<80 and(stock.actual_head_pad or STOCK.jump)or 0')
    before='or s.pose<68 or s.pose>78';assert text.count(before)==1;text=text.replace(before,'',1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        actual_stair_contact_then_original_Up=True,head_alignment_uses_actual_standing_state_on_any_native_height=True,
        head_underside96_uses_standing_A_other_heights_use_Up=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
