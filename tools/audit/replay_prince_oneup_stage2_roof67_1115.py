"""Release Up at measured roof height; action8 alone is not a roof witness."""
from functools import lru_cache
import replay_prince_oneup_stage2_mount67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='4d5b9dc5a4a7f99e25cda0b4c3e3a0478f882631e58fed888c0034212f258850'
    before='if s.action==8 or topped then';assert text.count(before)==2
    # The donor's legitimate animation/facing foot can lie31px left. The
    # subsequent neutral phase must still reach actual idle at112.
    text=text.replace(before,'if s.y_high==1 and math.abs(s.y-112)<=2 and s.foot>=143 and s.foot<=146 then')
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        release_Up_at_observed_roof_height_and_donor_foot_row=True,neutral_roof_idle_still_required=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
