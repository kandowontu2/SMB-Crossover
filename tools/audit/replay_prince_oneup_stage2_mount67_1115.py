"""Release the actual hoist on its admission, not a simultaneous Y sample."""
from functools import lru_cache
import replay_prince_oneup_stage2_level67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    old=Previous.controller(raw,mode,jump)
    assert C.digest(old.encode())=='268a7fe50e14c6ceb1b440debeba56154d93449f9475fc77af7c619551f22869'
    text=old
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    for name in('platform','coin'):
        old=f"  if s.action==8 and s.y<=114 then stock.{name}_mount=s;stockPhase('"+('two1-platform-release'if name=='platform'else'coin-ledge-release')+"',0)end"
        new="  local l,r=tile(s.x+2,144),tile(s.x+13,144)\n  local supported=(l~=95 and l~=96 and read(0xef36+l)&1~=0)or(r~=95 and r~=96 and read(0xef36+r)&1~=0)\n  local topped=s.action==49 and math.abs(s.y-112)<=2 and s.foot==144 and supported\n"+old.replace('s.action==8 and s.y<=114','s.action==8 or topped')
        change(old,new)
    change('stock.stage2_actor_milestones={};stock.stage2_hp_writes={}',
        'stock.stage2_actor_milestones={};stock.stage2_hp_writes={};stock.stage2_up_states={}')
    old=' local age=stock.prince_returns-stock.since\n'
    new=old+r''' if stock.phase=='two1-platform-up'or stock.phase=='coin-ledge-up'then
  local key=s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode
  if key~=stock.last_stage2_up and #stock.stage2_up_states<48 then
   stock.last_stage2_up=key;stock.stage2_up_states[#stock.stage2_up_states+1]={phase=stock.phase,state=s,left_tile144=tile(s.x+2,144),right_tile144=tile(s.x+13,144)}
  end
 end
'''
    change(old,new);LuaRuntime().compile(text)
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        release_Up_on_actual_hoist8_or_supported_top49=True,neutral_roof_idle_still_required=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
